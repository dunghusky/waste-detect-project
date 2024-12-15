import time
import cv2
import requests
import argparse
import os
from ultralytics import YOLO
import supervision as sv

from yolo_model.train import map_yolo_to_label
import matplotlib.pyplot as plt
from yolo_model.manage.StateManager import state
from yolo_model.manage.WebcamStream import WebcamStream
from supervision import Detections, BoxAnnotator, LineZone, LineZoneAnnotator, Point, ByteTrack
# from yolox.tracker.byte_tracker import BYTETracker, STrack
from onemetric.cv.utils.iou import box_iou_batch
from dataclasses import dataclass
from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
from config._timers import find_in_list
from config import _create_file
from yolo_model.controllers._upload_video_s3 import convert_video_to_mp4 as convert_mp4
from typing import List, Tuple

import numpy as np


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


def draw_boxes(frame, detections, box_annotator, lables_annatator, labels):
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

    return webcam_stream, fps


# ------------------------------------------------------------------------------#
class CustomSink:

    def __init__(self, LINE_START: Point, LINE_END: Point):
        # self.classes = classes
        self.tracker = sv.ByteTrack(minimum_matching_threshold=0.8)
        self.line_counter = LineZone(start=LINE_START, end=LINE_END)
        self.line_annotator = LineZoneAnnotator(
            thickness=4, text_thickness=4, text_scale=2
        )
        self.box_annatator, self.lables_annatator = initialize_yolo_and_annotators()

    def on_prediction(self, frame: VideoFrame, detections: sv.Detections) -> None:
        frame = frame.image.copy()
        detections = self.tracker.update_with_detections(detections=detections)
        # print("\n\n###Detection: ", detections)
        labels = [
            f"#{tracker_id} {class_name} {confidence:.2f}"
            for class_name, confidence, tracker_id in zip(
                detections["class_name"], detections.confidence, detections.tracker_id
            )
        ]

        frame = draw_boxes(frame, detections, self.box_annatator, self.lables_annatator, labels)
        self.line_counter.trigger(detections)
        self.line_annotator.annotate(frame=frame, line_counter=self.line_counter)

        # 6. Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        cv2.waitKey(1)


LINE_START = Point(670, 0)
LINE_END = Point(670, 750)

def main(
    rtsp_url: str,
    weights: str,
    device: str,
    confidence: float,
    iou: float,
) -> None:

    model = YOLO(weights)
    
    def inference_callback(frame: VideoFrame) -> sv.Detections:
        results = model(frame.image, verbose=False, conf=confidence, device=device)[0]
        return sv.Detections.from_ultralytics(results).with_nms(threshold=iou)

    sink = CustomSink(LINE_START=LINE_START, LINE_END=LINE_END)

    pipeline = InferencePipeline.init_with_custom_logic(
        video_reference=rtsp_url,
        on_video_frame=inference_callback,
        on_prediction=sink.on_prediction,
    )

    pipeline.start()

    try:
        pipeline.join()
    except KeyboardInterrupt:
        pipeline.terminate()

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Calculating detections dwell time in zones, using RTSP stream."
#     )
#     parser.add_argument(
#         "--rtsp_url",
#         type=str,
#         required=True,
#         # default="rtmp://45.90.223.138:12586/live"  python test.py --rtsp_url rtmp://45.90.223.138:12586/live
#         help="Complete RTSP URL for the video stream.",
#     )
#     parser.add_argument(
#         "--weights",
#         type=str,
#         default="./yolo_model/checkpoints/waste_detection_v2/weights/best.pt",
#         help="Path to the model weights file. Default is 'yolov8s.pt'.",
#     )
#     parser.add_argument(
#         "--device",
#         type=str,
#         default="cpu",
#         help="Computation device ('cpu', 'mps' or 'cuda'). Default is 'cpu'.",
#     )
#     parser.add_argument(
#         "--confidence_threshold",
#         type=float,
#         default=0.3,
#         help="Confidence level for detections (0 to 1). Default is 0.3.",
#     )
#     parser.add_argument(
#         "--iou_threshold",
#         default=0.7,
#         type=float,
#         help="IOU threshold for non-max suppression. Default is 0.7.",
#     )
#     # parser.add_argument(
#     #     "--classes",
#     #     nargs="*",
#     #     type=int,
#     #     default=[],
#     #     help="List of class IDs to track. If empty, all classes are tracked.",
#     # )
#     args = parser.parse_args()

#     main(
#         rtsp_url=args.rtsp_url,
#         weights=args.weights,
#         device=args.device,
#         confidence=args.confidence_threshold,
#         iou=args.iou_threshold,
#         # classes=args.classes,
#     )


# ----------------------------------------------------------------------------#


def send_to_hardware_api(waste_label):
    url = "http://127.0.0.1:8000/api/v1/stream/send-label"
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

waste_count = {
    "chai-lo-manh-vo-thuy-tinh": 0,
    "chai-nhua": 0,
    "hop-sua": 0,
    "khau-trang": 0,
    "lon-nuoc-giai-khat-bang-kim-loai": 0,
    "ly-nhua": 0,
    "rac-huu-co": 0,
    "tui-nilon":0
}

counted_ids = set()

# Đếm số frame để đặt tên file
def run_detection(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    frame_count = 0
    output_dir = "output_frames"  # Thư mục lưu trữ
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

    # 1. Khởi tạo mô hình YOLO và BoxAnnotator
    model, box_annatator, lables_annatator = initialize_yolo_and_annotators(
        "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"
    )

    # 2. Mở webcam và thiết lập các thông số
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    LINE_START = Point(670, 0)
    LINE_END = Point(670, 750)

    byte_tracker = sv.ByteTrack()

    CLASS_ID = [0, 1, 2, 3, 4, 5, 6, 7]

    line_counter = LineZone(start=LINE_START, end=LINE_END)
    line_annotator = LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)

    frame_generator = sv.get_video_frames_generator(stream_url)
    prev_in_count = 0
    prev_out_count = 0
    # frame_generator = VideoFrame()
    # 3. Vòng lặp chính để đọc khung hình từ webcam
    while True:
        # ret, frame = cap.read()
        for frame in frame_generator:
            detections = detect_objects(frame, model)

            detections = byte_tracker.update_with_detections(detections=detections)

            labels = [
                f"#{tracker_id} {class_name} {confidence:.2f}"
                for class_name, confidence, tracker_id in zip(
                    detections["class_name"], detections.confidence, detections.tracker_id
                )
            ]

            frame = draw_boxes(frame, detections, box_annatator, lables_annatator, labels)
            # line_counter.trigger(detections)
            line_counter.trigger(detections)

            if line_counter.out_count > prev_out_count:
                print("aaaaaaaaaaaaa")
                for class_name, tracker_id in zip(
                    detections["class_name"], detections.tracker_id
                ):
                    print("\n###Class_name: ", class_name)
                    print("\n###Tracker_id: ", tracker_id)
                    if tracker_id not in counted_ids:  # Nếu đối tượng chưa được đếm
                        counted_ids.add(tracker_id)  # Lưu tracker_id
                        if class_name in waste_count:
                            print("\n###Class_name: ", class_name)
                            waste_count[class_name] += 1
                            print("\n###Updated waste_count: ", waste_count)
                        else:
                            print("\nKhông có class_id")

                prev_out_count = line_counter.out_count

            line_annotator.annotate(frame=frame, line_counter=line_counter)

            # 6. Hiển thị khung hình
            cv2.imshow("YOLOv8 - RTMP Stream", frame)

            # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
            if cv2.waitKey(30) == 27:
                break


# def run_detection(stream_url):
#     """
#     Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
#     """
#     args = parse_args()
#     frame_width, frame_height = args.webcam_resolutions

#     frame_count = 0
#     output_dir = "output_frames"  # Thư mục lưu trữ
#     os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

#     # 1. Khởi tạo mô hình YOLO và BoxAnnotator
#     model, box_annatator, lables_annatator = initialize_yolo_and_annotators(
#         "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"
#     )

#     # 2. Mở webcam và thiết lập các thông số
#     cap = cv2.VideoCapture(stream_url)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#     LINE_START = Point(670, 0)
#     LINE_END = Point(670, 750)

#     byte_tracker = sv.ByteTrack()

#     CLASS_ID = [0, 1, 2, 3, 4, 5, 6, 7]

#     line_counter = LineZone(start=LINE_START, end=LINE_END)
#     line_annotator = LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)

#     frame_generator = sv.get_video_frames_generator(stream_url)
#     # 3. Vòng lặp chính để đọc khung hình từ webcam
#     while True:
#         # ret, frame = cap.read()
#         for frame in frame_generator:
#             detections = detect_objects(frame, model)

#             # if frame_count % 24 == 0:  # Lưu mỗi giây nếu fps = 30
#             #     plt.figure(figsize=(10, 6))  # Kích thước hình
#             #     plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Chuyển BGR sang RGB
#             #     plt.axis("on")  # Bật trục tọa độ
#             #     plt.title(f"Frame {frame_count}")  # Tiêu đề (nếu cần)

#             #     # Lưu hình ảnh
#             #     output_path = f"{output_dir}/frame_{frame_count}.png"
#             #     plt.savefig(output_path)
#             #     plt.close()  # Đóng figure để tránh chiếm bộ nhớ

#             # frame_count += 1
#             # if detections:
#             #     detections = byte_tracker.update_with_detections(detections=detections)
#             #     print("\n\n###Detection: ", detections)

#             #     if detections["class_name"] and detections.confidence and detections.tracker_id:
#             #         labels = [
#             #             f"#{tracker_id} {class_name} {confidence:.2f}"
#             #             for class_name, confidence, tracker_id in zip(
#             #                 detections["class_name"], detections.confidence, detections.tracker_id
#             #             )
#             #         ]
#             #     else:
#             #         labels = []

#             #     frame = draw_boxes(frame, detections, box_annatator, lables_annatator, labels)
#             #     line_counter.trigger(detections)
#             #     print("\n\n###Line in: ", line_counter.in_count)
#             #     print("\n\n###Line out: ", line_counter.out_count)
#             # else:
#             #     print("No detections.")
#             #     labels = []
#             # frame_count += 1
#             # if detections:
#             #     detections = byte_tracker.update_with_detections(detections=detections)
#             #     print("\n\n###Detection: ", detections)

#             detections = byte_tracker.update_with_detections(detections=detections)
#             print("\n\n###Detection: ", detections)
#             labels = [
#                 f"#{tracker_id} {class_name} {confidence:.2f}"
#                 for class_name, confidence, tracker_id in zip(
#                     detections["class_name"],
#                     detections.confidence,
#                     detections.tracker_id,
#                 )
#             ]

#             frame = draw_boxes(
#                 frame, detections, box_annatator, lables_annatator, labels
#             )
#             line_counter.trigger(detections)
#             print("\n###Line in: ", line_counter.in_count)
#             print("\n###Line out: ", line_counter.out_count)
#             line_annotator.annotate(frame=frame, line_counter=line_counter)

#             # 6. Hiển thị khung hình
#             cv2.imshow("YOLOv8 - RTMP Stream", frame)

#             # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
#             if cv2.waitKey(30) == 27:
#                 break


# # Chạy chương trình
if __name__ == "__main__":
    # run_detection("rtmp://45.90.223.138:12586/live")
    run_detection("./output_frames/6779842421098717812.mp4")
