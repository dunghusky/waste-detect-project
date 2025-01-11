import os
import time
import cv2
from fastapi import WebSocket
import supervision as sv
from ultralytics import YOLO
import uuid

from yolo_model.controllers._stream_detect import detect_objects, initialize_yolo_and_annotators
from config import _constants
from yolo_model.controllers import _upload_s3

def detect_image(img_path, model_path, output_path, conf=0.1, iou=0.5):
    frame = cv2.imread(img_path)
    if frame is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {img_path}")
    (
        model,
        box_annatator,
        lables_annatator,
        line_counter,
        line_annotator,
        byte_tracker,
    ) = initialize_yolo_and_annotators(
        model_path, _constants.LINE_START, _constants.LINE_END
    )
    # print("Model: ", model)
    detections = detect_objects(frame, model, conf, iou)
    # print("\nDetection: ", detections)
    
    detection_results = []
    for xyxy, confidence, class_id, class_name in zip(
        detections.xyxy, detections.confidence, detections.class_id, detections["class_name"]
    ):
        detection_results.append({
            "x": round(xyxy[0]),
            "y": round(xyxy[1]),
            "width": round(xyxy[2] - xyxy[0]),
            "height": round(xyxy[3] - xyxy[1]),
            "confidence": round(float(confidence), 3), 
            "class": class_name,
            "class_id": int(class_id)
        })
    
    labels = [
        f"#{class_name} {confidence:.2f}"
        for class_name, confidence in zip(
            detections["class_name"], detections.confidence
        )
    ]
    frame = box_annatator.annotate(detections=detections, scene=frame)
    frame = lables_annatator.annotate(labels=labels, scene=frame, detections=detections)

    os.makedirs(output_path, exist_ok=True)

    output_filename = f"detected_{uuid.uuid4().hex}.jpg"
    temp_image_path = os.path.join(output_path, output_filename)

    cv2.imwrite(temp_image_path, frame)

    try:
        link_img = _upload_s3.upload_file_to_s3(temp_image_path)
        img_url = _upload_s3.convert_cloudfront_link(link_img)

    finally:
        # Xóa ảnh tạm thời để tiết kiệm dung lượng
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return img_url, detection_results


def generate_stream_with_detection(video_path, model_path, conf=0.1, iou=0.5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Không thể mở video từ đường dẫn: {video_path}")

    # Khởi tạo YOLO và annotator
    (
        model,
        box_annatator,
        lables_annatator,
        line_counter,
        line_annotator,
        byte_tracker,
    ) = initialize_yolo_and_annotators(model_path, _constants.LINE_START, _constants.LINE_END)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Dò vật thể
            detections = detect_objects(frame, model, conf, iou)

            # # Gửi JSON qua WebSocket
            # frame_predictions = []
            # for xyxy, confidence, class_id, class_name in zip(
            #     detections.xyxy, detections.confidence, detections.class_id, detections["class_name"]
            # ):
            #     frame_predictions.append({
            #         "class": class_name,
            #         "confidence": round(float(confidence), 3),
            #         "bbox": {
            #             "x": round(xyxy[0]),
            #             "y": round(xyxy[1]),
            #             "width": round(xyxy[2] - xyxy[0]),
            #             "height": round(xyxy[3] - xyxy[1]),
            #         },
            #         "color": "#00FFCE",  # Ví dụ gán màu cho box
            #     })

            # await websocket.send_json({"predictions": frame_predictions})

            # Vẽ và mã hóa frame
            if detections is not None:
                frame = box_annatator.annotate(detections=detections, scene=frame)
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            # Truyền MJPEG frame
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

            time.sleep(0.03)
    finally:
        cap.release()