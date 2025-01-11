import time
import cv2
import requests
import argparse

from ultralytics import YOLO
import supervision as sv
import config._setup_bytetrack

from yolo_model.train import map_yolo_to_label
from yolo_model.manage.StateManager import state
from yolo_model.manage.WebcamStream import WebcamStream
from yolo_model.manage.YOLOWorker import YOLOWorker
from supervision import Detections, BoxAnnotator, LineZone, LineZoneAnnotator, Point
from yolox.tracker.byte_tracker import BYTETracker, STrack
from onemetric.cv.utils.iou import box_iou_batch
from dataclasses import dataclass
from config import _create_file
from yolo_model.controllers._upload_s3 import convert_video_to_mp4 as convert_mp4
from typing import List

import numpy as np


@dataclass(frozen=True)
class BYTETrackerArgs:
    track_thresh: float = 0.25
    track_buffer: int = 30
    match_thresh: float = 0.8
    aspect_ratio_thresh: float = 3.0
    min_box_area: float = 1.0
    mot20: bool = False


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
# converts Detections into format that can be consumed by match_detections_with_tracks function
def detections2boxes(detections: Detections) -> np.ndarray:
    return np.hstack((detections.xyxy, detections.confidence[:, np.newaxis]))


# converts List[STrack] into format that can be consumed by match_detections_with_tracks function
def tracks2boxes(tracks: List[STrack]) -> np.ndarray:
    return np.array([track.tlbr for track in tracks], dtype=float)


# matches our bounding boxes with predictions
def match_detections_with_tracks(
    detections: Detections, tracks: List[STrack]
) -> Detections:
    if not np.any(detections.xyxy) or len(tracks) == 0:
        return np.empty((0,))

    tracks_boxes = tracks2boxes(tracks=tracks)
    iou = box_iou_batch(tracks_boxes, detections.xyxy)
    track2detection = np.argmax(iou, axis=1)

    tracker_ids = [None] * len(detections)

    for tracker_index, detection_index in enumerate(track2detection):
        if iou[tracker_index, detection_index] != 0:
            tracker_ids[detection_index] = tracks[tracker_index].track_id

    return tracker_ids


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

    video_writer = state.get_video_writer()
    if not video_writer or not video_writer.isOpened():
        raise ValueError("VideoWriter không được khởi tạo đúng cách.")

    # Khởi tạo mô hình YOLO và các công cụ hỗ trợ
    model, box_annatator, lables_annatator = initialize_yolo_and_annotators(
        "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"
    )

    LINE_START = Point(50, 1500)
    LINE_END = Point(3840-50, 1500)

    byte_tracker = BYTETracker(BYTETrackerArgs())

    CLASS_ID = [0, 1, 2, 3, 4, 5, 6, 7]

    line_counter = LineZone(start=LINE_START, end=LINE_END)
    line_annotator = LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)

    try:
        while not state.terminate_flag:
            if state.terminate_flag:  # Kiểm tra cờ dừng
                break

            start_time = time.time()

            frame = cap.read()

            if frame is None:
                print("Không nhận được khung hình.")
                break

            # Xử lý nhận diện với YOLO
            detections = detect_objects(frame, model)

            # mask = np.array([class_id in CLASS_ID for class_id in detections["class_id"]], dtype=bool)
            # detections.filter(mask=mask, inplace=True)

            # tracking detections
            tracks = byte_tracker.update(
                output_results=detections2boxes(detections=detections),
                img_info=frame.shape,
                img_size=frame.shape
            )
            tracker_id = match_detections_with_tracks(detections=detections, tracks=tracks)
            detections.tracker_id = np.array(tracker_id)

            # # filtering out detections without trackers
            # mask = np.array([tracker_id is not None for tracker_id in detections.tracker_id], dtype=bool)
            # detections.filter(mask=mask, inplace=True)

            # # updating line counter
            # line_counter.update(detections=detections)

            # Vẽ kết quả lên khung hình
            frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

            # line_annotator.annotate(frame=frame, line_counter=line_counter)

            end_time = time.time()

            latency = end_time - start_time
            print(f"Độ trễ xử lý: {latency:.3f} giây")

            video_writer = state.get_video_writer()
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
        cap.stop()
        video_writer = state.get_video_writer()
        if video_writer:
            video_writer.release()
        state.set_video_writer(None)
        state.completed_event.set()  # Báo hiệu đã hoàn tất


# Chạy chương trình
# if __name__ == "__main__":
#     generate_stream("rtmp://45.90.223.138:1256/live")
