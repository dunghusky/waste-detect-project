import os
import cv2
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

    return img_url
