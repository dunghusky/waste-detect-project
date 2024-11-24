from datetime import datetime
import cv2
import requests
import argparse
import httpx

from ultralytics import YOLO
import supervision as sv

from yolo_model.train import map_yolo_to_label
from yolo_model.manage.StateManager import state
from config import _create_file


def parse_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(description="Yolov8 live camera")
    parse.add_argument("--webcam_resolutions", type=int, default=[640, 480], nargs=2)
    args = parse.parse_args()
    return args


def detect_objects(frame, model):
    """
    Nhận diện vật thể trên khung hình hiện tại.
    Args:
    - frame: Khung hình hiện tại từ video.
    - model: Mô hình YOLO đã được tải.

    Returns:
    - detections: Kết quả nhận diện.
    """
    results = model(frame)[0]
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
    labels = [
        f"{class_name} {confidence:.2f}"
        for class_name, confidence in zip(
            detections["class_name"], detections.confidence
        )
    ]
    frame = box_annotator.annotate(detections=detections, scene=frame)

    frame = lables_annatator.annotate(labels=labels, scene=frame, detections=detections)

    return frame


def initialize_yolo_and_annotators(model_path: str):
    """
    Khởi tạo mô hình YOLO và các annotator.
    """
    model = YOLO(model_path)
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_thickness=4, text_scale=1)
    return model, box_annotator, label_annotator


def initialize_video_stream(stream_url: str, frame_width: int, frame_height: int):
    """
    Mở luồng video từ URL và thiết lập độ phân giải.
    """
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    if not cap.isOpened():
        raise ValueError(f"Không thể mở luồng video từ URL: {stream_url}")

    return cap
# ----------------------------------------------------------------------------#

def send_to_hardware_api(waste_label):
    url = "http://192.168.1.13:8000/update"
    payload = {"label": waste_label}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Gửi nhãn thành công:", waste_label)
        else:
            print("Lỗi khi gửi nhãn:", response.status_code, response.text)
    except Exception as e:
        print("Lỗi kết nối tới API:", e)


def generate_stream(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # Tạo tên file video với timestamp
    state.output_file = _create_file.create_video()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    state.set_video_writer(
        cv2.VideoWriter(state.output_file, fourcc, 20.0, (frame_width, frame_height))
    )
    
    video_writer = state.get_video_writer()
    if not video_writer or not video_writer.isOpened():
        raise ValueError("VideoWriter không được khởi tạo đúng cách.")

    # Khởi tạo mô hình YOLO và các công cụ hỗ trợ
    model, box_annatator, lables_annatator = initialize_yolo_and_annotators(
        "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"
    )

    # Mở luồng video
    cap = initialize_video_stream(stream_url, frame_width, frame_height)

    if not cap.isOpened():
        raise ValueError(f"Không thể mở stream từ URL: {stream_url}")

    try:
        while not state.terminate_flag:
            if state.terminate_flag:  # Kiểm tra cờ dừng
                break

            ret, frame = cap.read()
            if not ret:
                print("Không nhận được khung hình.")
                break

            # Xử lý nhận diện với YOLO
            detections = detect_objects(frame, model)

            # Gửi nhãn đến phần cứng qua API
            # for class_name, confidence in zip(
            #     detections["class_name"], detections.confidence
            # ):
            #     waste_label = map_yolo_to_label.map_yolo_to_label(class_name)
            #     if waste_label != -1:
            #         print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")
            #         send_to_hardware_api(waste_label)

            # Vẽ kết quả lên khung hình
            frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

            video_writer = state.get_video_writer()
            if video_writer is not None:
                video_writer.write(frame)

            # Mã hóa khung hình sang JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            # Truyền dữ liệu MJPEG
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            if (
                cv2.waitKey(1) == 27 or state.terminate_flag
            ):  # Exit when ESC key is pressed or terminate flag is set
                break

    finally:
        cap.release()
        video_writer = state.get_video_writer()
        if video_writer:
            video_writer.release()
        state.set_video_writer(None)
        state.completed_event.set()  # Báo hiệu đã hoàn tất


# ----------------------------------------------------------------------------#
# def generate_stream(stream_url):
#     """
#     Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
#     """
#     args = parse_args()
#     frame_width = 600
#     frame_height = 800 #args.webcam_resolutions

#     # Tạo tên file video với timestamp
#     state.output_file = _create_file.create_video()
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     state.set_video_writer(
#         cv2.VideoWriter(state.output_file, fourcc, 20.0, (frame_width, frame_height))
#     )
#     video_writer = state.get_video_writer()
#     if not video_writer or not video_writer.isOpened():
#         raise ValueError("VideoWriter không được khởi tạo đúng cách.")

#     # Khởi tạo mô hình YOLO và các công cụ hỗ trợ
#     model, box_annatator, lables_annatator  = initialize_yolo_and_annotators("./yolo_model/checkpoints/waste_detection_v2/weights/best.pt")

#     # Mở luồng video
#     cap = initialize_video_stream(stream_url, frame_width, frame_height)

#     if not cap.isOpened():
#         raise ValueError(f"Không thể mở stream từ URL: {stream_url}")

#     while True:
#         if state.terminate_flag:  # Kiểm tra cờ dừng
#             break

#         ret, frame = cap.read()
#         if not ret:
#             print("Không nhận được khung hình.")
#             break

#         # Xử lý nhận diện với YOLO
#         detections = detect_objects(frame, model)

#         # Gửi nhãn đến phần cứng qua API
#         # for class_name, confidence in zip(
#         #     detections["class_name"], detections.confidence
#         # ):
#         #     waste_label = map_yolo_to_label.map_yolo_to_label(class_name)
#         #     if waste_label != -1:
#         #         print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")
#         #         send_to_hardware_api(waste_label)

#         # Vẽ kết quả lên khung hình
#         frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

#         video_writer = state.get_video_writer()
#         if video_writer is not None:
#             video_writer.write(frame)

#         # Mã hóa khung hình sang JPEG
#         _, buffer = cv2.imencode(".jpg", frame)
#         frame_bytes = buffer.tobytes()

#         # Truyền dữ liệu MJPEG
#         yield (
#             b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
#         )
#         if (
#             cv2.waitKey(1) == 27 or state.terminate_flag
#         ):  # Exit when ESC key is pressed or terminate flag is set
#             break

#     cap.release()
#     video_writer = state.get_video_writer()
#     if video_writer is not None:
#         video_writer.release()
#     print(f"Stream đã dừng. Video đã được lưu tại {state.output_file}")


# # ----------------------------------------------------------------------------#

def run_detection_1(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # 1. Khởi tạo mô hình YOLO và BoxAnnotator
    model = YOLO(
        "E:/HocTap/graduation_project/waste-detect-project/train_data/checkpoints/waste_detection_v2/weights/best.pt"
    )
    box_annatator = sv.BoxAnnotator(thickness=2)
    lables_annatator = sv.LabelAnnotator(text_thickness=4, text_scale=1)

    # 2. Mở webcam và thiết lập các thông số
    # cap = cv2.VideoCapture(1)
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # 3. Vòng lặp chính để đọc khung hình từ webcam
    while True:
        ret, frame = cap.read()
        # if not ret:
        #     print("Không nhận được khung hình (frame). Kết nối có thể đã bị ngắt.")
        #     break
        detections = detect_objects(frame, model)

        for class_name, confidence in zip(
            detections["class_name"], detections.confidence
        ):
            waste_label = map_yolo_to_label.map_yolo_to_label(class_name)

            if waste_label != -1:
                print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")
                # send_to_hardware(ser, waste_label)

        frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

        # 6. Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        if cv2.waitKey(30) == 27:
            break

# Chạy chương trình
if __name__ == "__main__":
    run_detection_1("rtmp://82.180.160.47:1888/live")
