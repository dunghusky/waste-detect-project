import asyncio
import cv2
import numpy as np
import argparse

from ultralytics import YOLO
import supervision as sv

from connect_webcam import map_yolo_to_label


def parse_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(description="Yolov8 live camera")
    parse.add_argument("--webcam_resolutions", type=int, default=[1280, 720], nargs=2)
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


def run_detection_1(stream_url):
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # 1. Khởi tạo mô hình YOLO và BoxAnnotator
    model = YOLO(
        "./checkpoints/waste_detection_v2/weights/best.pt"
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
    return waste_label


async def run_detection(stream_url, websocket=None):
    """
    Hàm chính để thực hiện nhận diện và xử lý kết quả.
    Hỗ trợ:
    - Trả về nhãn cho phần cứng.
    - Stream video đã xử lý (qua WebSocket nếu được cung cấp).
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # 1. Khởi tạo mô hình YOLO và BoxAnnotator
    model = YOLO("./checkpoints/waste_detection_v2/weights/best.pt")
    box_annatator = sv.BoxAnnotator(thickness=2)
    lables_annatator = sv.LabelAnnotator(text_thickness=4, text_scale=1)

    # 2. Mở luồng video
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # 3. Vòng lặp chính để xử lý từng khung hình
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Không nhận được khung hình (frame). Kết nối có thể đã bị ngắt.")
            break

        detections = detect_objects(frame, model)

        for class_name, confidence in zip(
            detections["class_name"], detections.confidence
        ):
            waste_label = map_yolo_to_label.map_yolo_to_label(class_name)

            if waste_label != -1:
                print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")
                # Gửi nhãn qua WebSocket (nếu có client kết nối)
                if websocket:
                    await websocket.send_json({"label": waste_label})

        # Vẽ bounding boxes lên khung hình
        frame = draw_boxes(frame, detections, box_annatator, lables_annatator)

        # Gửi khung hình qua WebSocket (nếu có client kết nối)
        if websocket:
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())

        # Hiển thị khung hình (cho mục đích debug hoặc kiểm tra)
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn ESC để thoát
        if cv2.waitKey(30) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# Chạy chương trình
if __name__ == "__main__":
    run_detection()
