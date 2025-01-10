from copy import deepcopy
import time
import cv2
import requests
import argparse
import torch

from ultralytics import YOLO
import supervision as sv

from yolo_model.train import map_yolo_to_label
from yolo_model.manage.StateManager import state
from yolo_model.manage.WebcamStream import WebcamStream
from config import _create_file, _constants
from yolo_model.controllers._upload_s3 import convert_video_to_mp4 as convert_mp4


def parse_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(description="Yolov8 live camera")
    parse.add_argument("--webcam_resolutions", type=int, default=[640, 480], nargs=2)
    args = parse.parse_args()
    return args


def detect_objects(frame, model, conf=0.1, iou=0.5):
    """
    Nhận diện vật thể trên khung hình hiện tại.
    Args:
    - frame: Khung hình hiện tại từ video.
    - model: Mô hình YOLO đã được tải.

    Returns:
    - detections: Kết quả nhận diện.
    """
    # results = model(frame)[0]
    results = model.predict(frame, conf=conf, iou=iou)[0]
    detections = sv.Detections.from_ultralytics(results)
    return detections


def draw_boxes(frame, detections, box_annotator, lables_annatator):
    """
    Vẽ khung hộp và hiển thị nhãn lên khung hình.
    Args:
    - frame: Khung hình hiện tại.
    - detections: Đối tượng `Detections` từ YOLO.
    - box_annotator: Đối tượng để vẽ khung hộp.
    - model: Mô hình YOLO để lấy tên nhãn.

    Returns:
    - frame: Khung hình đã được vẽ khung hộp và nhãn.
    """

    # Kiểm tra detections trước khi xử lý
    if detections is None or detections["class_name"] is None: #or not any(detections["class_name"])
        print("\nDetection draw: ", detections["class_name"])
        print("Không có đối tượng để vẽ.")
        return frame  # Trả về khung hình gốc

    labels = [
        f"#{tracker_id} {class_name} {confidence:.2f}"
        for class_name, confidence, tracker_id in zip(
            detections["class_name"], detections.confidence, detections.tracker_id
        )
    ]
    frame = box_annotator.annotate(detections=detections, scene=frame)

    frame = lables_annatator.annotate(labels=labels, scene=frame, detections=detections)

    return frame


def initialize_yolo_and_annotators(
    model_path: str, LINE_START: sv.Point, LINE_END: sv.Point
):
    """
    Khởi tạo mô hình YOLO và các annotator.
    """
    device = "cuda:1" if torch.cuda.is_available() else "cpu"
    print("Thiết bị đang được sử dụng:", device)
    
    model = YOLO(model_path).to(device)

    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_thickness=4, text_scale=1)
    line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=2, text_scale=2)
    byte_tracker = sv.ByteTrack()
    return (
        model,
        box_annotator,
        label_annotator,
        line_counter,
        line_annotator,
        byte_tracker,
    )


def initialize_video_stream(stream_url: str):
    """
    Mở luồng video từ URL và thiết lập độ phân giải.
    """
    webcam_stream = WebcamStream(stream_id=stream_url)
    webcam_stream.start()

    actual_width = webcam_stream.vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = webcam_stream.vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(
        f"Kích thước thực tế của luồng video: {int(actual_width)}x{int(actual_height)}"
    )

    fps = webcam_stream.vcap.get(cv2.CAP_PROP_FPS)  # Lấy FPS thực tế từ webcam stream
    print(f"FPS của webcam/video stream: {fps}")
    # cap = cv2.VideoCapture()
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # if not cap.isOpened():
    #     raise ValueError(f"Không thể mở luồng video từ URL: {stream_url}")

    return webcam_stream, fps


# ----------------------------------------------------------------------------#


def send_to_hardware_api(waste_label):
    url = "http://52.88.216.148:8000/api/v1/stream/send-label"
    payload = {"label": waste_label}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Gửi nhãn thành công:", waste_label)
        else:
            print("Lỗi khi gửi nhãn:", response.status_code, response.text)
    except Exception as e:
        print("Lỗi kết nối tới API:", e)


# ----------------------------------------------------------------------------#
def generate_stream(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # Mở luồng video
    cap, fps = initialize_video_stream(stream_url)

    # Tạo tên file video với timestamp
    state.output_file = _create_file.create_video()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    state.set_video_writer(
        cv2.VideoWriter(state.output_file, fourcc, 26.0, (frame_width, frame_height))
    )

    repeat_frames = 3

    video_writer = state.get_video_writer()
    if not video_writer or not video_writer.isOpened():
        raise ValueError("VideoWriter không được khởi tạo đúng cách.")

    # Khởi tạo mô hình YOLO và các công cụ hỗ trợ
    (
        model,
        box_annatator,
        lables_annatator,
        line_counter,
        line_annotator,
        byte_tracker,
    ) = initialize_yolo_and_annotators(
        _constants.MODEL_PATH_3, _constants.LINE_START, _constants.LINE_END
    )

    state.waste_count = deepcopy(_constants.WASTE_COUNT)

    prev_in_count = 0
    prev_out_count = 0

    # Biến theo dõi FPS thực tế
    frame_count = 0

    try:
        while not state.terminate_flag:
            if state.terminate_flag:  # Kiểm tra cờ dừng
                break

            start_time = time.time()

            frame = cap.read()

            if frame is None:
                print("Không nhận được khung hình.")
                break

            # Tăng số lượng khung hình đã xử lý
            frame_count += 1

            # # Đợi nếu cần để giữ đồng bộ FPS
            # elapsed_time = time.time() - start_time
            # if elapsed_time < 1.0 / fps:
            #     time.sleep(1.0 / fps - elapsed_time)

            # Xử lý nhận diện với YOLO
            detections = detect_objects(frame, model)

            # Kiểm tra detections trước khi tiếp tục
            if detections is not None and len(detections["class_name"]) > 0:
                # print("\nKiểu dữ liệu: ", detections["class_name"])
                # print("\nLen: ", len(detections["class_name"]))
                detections = byte_tracker.update_with_detections(detections=detections)

                # Vẽ kết quả lên khung hình
                frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

                line_counter.trigger(detections)

                if line_counter.out_count > prev_out_count:
                    print("\n line_counter.out_count: ", line_counter.out_count)
                    for class_name, tracker_id in zip(
                        detections["class_name"], detections.tracker_id
                    ):
                        print("\n###Class_name: ", class_name)
                        print("\n###Tracker_id: ", tracker_id)
                        if tracker_id in _constants.COUNTED_IDS:
                            continue  # Bỏ qua nếu tracker_id đã được xử lý
                        # if tracker_id not in _constants.COUNTED_IDS:  # Nếu đối tượng chưa được đếm
                        _constants.COUNTED_IDS.add(tracker_id)  # Lưu tracker_id
                        if class_name in state.waste_count:
                            print("\n###Class_name: ", class_name)
                            state.waste_count[class_name] += 1
                            print("\n###Updated waste_count: ", state.waste_count)
                            waste_label = map_yolo_to_label.map_yolo_to_label(
                                class_name
                            )
                            print("\nwaste_label: ", waste_label)
                            if waste_label != -1:
                                print(
                                    f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}"
                                )
                                send_to_hardware_api(waste_label)
                        else:
                            print("\nKhông có class_id")

                    prev_out_count = line_counter.out_count

                else:
                    # Nếu không có đối tượng, tiếp tục pipeline nhưng không cập nhật detections
                    print("Không có đối tượng nào được nhận diện.")

            line_annotator.annotate(frame=frame, line_counter=line_counter)

            end_time = time.time()

            latency = end_time - start_time
            print(f"Độ trễ xử lý: {latency:.3f} giây")

            video_writer = state.get_video_writer()
            # Trong vòng lặp chính
            for _ in range(repeat_frames):
                if video_writer is not None:
                    video_writer.write(frame)

            # Mã hóa khung hình sang JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            # Truyền dữ liệu MJPEG
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            if (
                cv2.waitKey(1) == 27 or state.terminate_flag
            ):  # Exit when ESC key is pressed or terminate flag is set
                break

    finally:
        if cap is not None:
            cap.stop()
        video_writer = state.get_video_writer()
        if video_writer:
            video_writer.release()
        state.set_video_writer(None)
        state.completed_event.set()  # Báo hiệu đã hoàn tất


# Chạy chương trình
# if __name__ == "__main__":
#     # generate_stream("rtmp://82.180.160.47:1888/live")
