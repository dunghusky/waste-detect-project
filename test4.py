from copy import deepcopy
import cv2
from dotenv import load_dotenv
import requests
import argparse
import torch
import numpy as np

from ultralytics import YOLO
import supervision as sv

from yolo_model.manage.StateManager import state
from yolo_model.manage.WebcamStream import WebcamStream
from config import _constants
import inference
import os

load_dotenv()

key_robo = os.getenv("ROBOFLOW_API_KEY")


def convert_xywh_to_xyxy(detections):
    """
    Chuyển đổi tọa độ bounding box từ (x, y, width, height) sang (x_min, y_min, x_max, y_max).
    Args:
    - detections: Danh sách các ObjectDetectionInferenceResponse từ Roboflow.

    Returns:
    - xyxy: Danh sách tọa độ bounding box ở định dạng [x_min, y_min, x_max, y_max].
    """
    xyxy = []
    confidences = []
    class_ids = []
    class_names = []

    # Duyệt qua từng response trong danh sách detections
    for response in detections:
        for pred in response.predictions:  # Duyệt qua từng prediction
            x_min = pred.x - pred.width / 2
            y_min = pred.y - pred.height / 2
            x_max = pred.x + pred.width / 2
            y_max = pred.y + pred.height / 2
            xyxy.append([x_min, y_min, x_max, y_max])
            confidences.append(pred.confidence)
            class_ids.append(pred.class_id)
            class_names.append(pred.class_name)

    return xyxy, confidences, class_ids, class_names


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
    - model: Mô hình được tải từ Roboflow.

    Returns:
    - Detections: Kết quả nhận diện ở định dạng sv.Detections hoặc None nếu không phát hiện.
    """

    # Nhận dữ liệu dự đoán từ Roboflow
    detections = model.infer(image=frame, confidence=0.05, iou_threshold=0.5)

    # Chuyển đổi bounding box sang định dạng xyxy và thu thập thông tin khác
    xyxy_boxes, confidences, class_ids, class_names = convert_xywh_to_xyxy(detections)

    # Kiểm tra nếu không có bounding box nào được phát hiện
    if len(xyxy_boxes) == 0:
        return None

    # Chuyển đổi sang numpy array
    xyxy_boxes_np = np.array(xyxy_boxes, dtype=np.float32)
    confidences_np = np.array(confidences, dtype=np.float32)
    class_ids_np = np.array(class_ids, dtype=np.int32)

    # Chuẩn bị dữ liệu đầu ra dưới dạng sv.Detections
    result = sv.Detections(
        xyxy=xyxy_boxes_np, confidence=confidences_np, class_id=class_ids_np
    )
    result.data["class_name"] = class_names  # Thêm thông tin tên lớp

    return result


# def detect_objects(frame, model):
#     """
#     Nhận diện vật thể trên khung hình hiện tại.
#     Args:
#     - frame: Khung hình hiện tại từ video.
#     - model: Mô hình YOLO đã được tải.

#     Returns:
#     - detections: Kết quả nhận diện.
#     """
#     # results = model(frame)[0]
#     # results = model.predict(frame, conf=0.1, iou=0.5)[0]
#     # detections = sv.Detections.from_ultralytics(results)
#     results = model.infer(image=frame, confidence=0.1, iou_threshold=0.5)
#     detections = sv.Detections.from_ultralytics(results)
#     return detections


# def draw_boxes(frame, detections, box_annotator, lables_annatator):
#     """
#     Vẽ khung hộp và hiển thị nhãn lên khung hình.
#     Args:
#     - frame: Khung hình hiện tại.
#     - detections: Đối tượng `Detections` từ YOLO.
#     - box_annotator: Đối tượng để vẽ khung hộp.
#     - model: Mô hình YOLO để lấy tên nhãn.

#     Returns:
#     - frame: Khung hình đã được vẽ khung hộp và nhãn.
#     """

#     # Kiểm tra detections trước khi xử lý
#     # if (
#     #     detections is None or detections["class_name"] is None
#     # ):  # or not any(detections["class_name"])
#     #     return frame  # Trả về khung hình gốc
#     if not detections["xyxy"]:
#         return frame

#     labels = [
#         # f"#{tracker_id} {class_name}"
#         # for class_name, confidence, tracker_id in zip(
#         #     detections["class_name"], detections.confidence, detections.tracker_id
#         # )
#         f"{detections['class_name'][i]}: {detections['confidence'][i]:.2f}"
#         for i in range(len(detections["xyxy"]))
#     ]
#     for i, box in enumerate(detections["xyxy"]):
#         box_annotator.annotate(scene=frame, detections=sv.Detections(xyxy=[box]))
#     # frame = box_annotator.annotate(detections=detections, scene=frame)

#     lables_annatator.annotate(labels=labels, scene=frame, detections=detections)

#     return frame


def draw_boxes(frame, detections, box_annotator, label_annotator):
    """
    Vẽ khung hộp và hiển thị nhãn lên khung hình.
    Args:
    - frame: Khung hình hiện tại.
    - detections: Đối tượng Detections từ YOLO.
    - box_annotator: Đối tượng để vẽ khung hộp.
    - label_annotator: Đối tượng để gắn nhãn.

    Returns:
    - frame: Khung hình đã được vẽ khung hộp và nhãn.
    """
    if len(detections.xyxy) == 0:
        return frame

    # Chuẩn bị nhãn
    labels = [
        f"{detections.tracker_id[i]}: {detections.data['class_name'][i]}: {detections.confidence[i]:.2f}"
        for i in range(len(detections.xyxy))
    ]

    # Vẽ bounding box
    frame = box_annotator.annotate(scene=frame, detections=detections)

    # Gắn nhãn
    frame = label_annotator.annotate(labels=labels, scene=frame, detections=detections)

    return frame


def initialize_yolo_and_annotators(
    model_path: str, LINE_START: sv.Point, LINE_END: sv.Point, key: str
):
    """
    Khởi tạo mô hình YOLO và các annotator.
    """
    # device = "cuda:1" if torch.cuda.is_available() else "cpu"
    # print("Thiết bị đang được sử dụng:", device)

    # model = YOLO(model_path).to(device)
    model = inference.get_model(model_path, key)

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
# Đếm số frame để đặt tên file
def run_detection(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # Mở luồng video
    cap, fps = initialize_video_stream(stream_url)

    # Khởi tạo mô hình YOLO và các công cụ hỗ trợ
    (
        model,
        box_annatator,
        lables_annatator,
        line_counter,
        line_annotator,
        byte_tracker,
    ) = initialize_yolo_and_annotators(
        "phan-loai-rac-m7npu/8", _constants.LINE_START, _constants.LINE_END, key_robo
    )

    while True:
        frame = cap.read()

        detections = detect_objects(frame, model)

        # Nếu không có đối tượng, tiếp tục vòng lặp
        if detections is not None:
            detections = byte_tracker.update_with_detections(detections=detections)
            print("\nDetection: ", detections)

            # frame = draw_boxes(frame, detections, box_annatator, lables_annatator)
            frame = draw_boxes(frame, detections, box_annatator, lables_annatator)
            # line_counter.trigger(detections)
            line_counter.trigger(detections)

        line_annotator.annotate(frame=frame, line_counter=line_counter)

        # 6. Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        if cv2.waitKey(30) == 27:
            break


# Chạy chương trình
if __name__ == "__main__":
    run_detection("rtmp://52.88.216.148:12566/live")
    # run_detection("./output_frames/6779842421098717812.mp4")
