import cv2
import numpy as np
import argparse

from ultralytics import YOLO
import supervision as sv


def parse_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(description="Yolov8 live camera")
    parse.add_argument("--webcam_resolutions", type=int, default=[1280, 720], nargs=2)
    args = parse.parse_args()
    return args


def main():
    args = parse_args()
    # # Thay đổi đường dẫn source thành địa chỉ RTMP của bạn
    # rtmp_url = "rtmp://54.92.211.110:1965/live"
    frame_width, frame_height = args.webcam_resolutions
    # Khởi tạo VideoCapture với đường dẫn RTMP
    # cap = cv2.VideoCapture(rtmp_url)
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("yolov8l.pt")
    box_annatator = sv.BoxAnnotator(thickness=2)
    lables_annatator = sv.LabelAnnotator(text_thickness=4, text_scale=1)
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # Kiểm tra xem việc mở luồng RTMP có thành công không
    # if not cap.isOpened():
    #     print(f"Không thể mở luồng video từ {rtmp_url}")
    #     return

    while True:
        ret, frame = cap.read()
        # if not ret:
        #     print("Không nhận được khung hình (frame). Kết nối có thể đã bị ngắt.")
        #     break
        result = model(frame)[0]
        detections = sv.Detections.from_ultralytics(result)

        labels = [
            f"{class_name} {confidence:.2f}"
            for class_name, confidence in zip(
                detections["class_name"], detections.confidence
            )
        ]

        frame = box_annatator.annotate(detections=detections, scene=frame)

        frame = lables_annatator.annotate(
            labels=labels, scene=frame, detections=detections
        )
        # Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        if cv2.waitKey(30) == 27:
            break

    # Giải phóng tài nguyên sau khi kết thúc
    # cap.release()
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
