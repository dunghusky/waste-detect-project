import cv2
import numpy as np
import argparse

from ultralytics import YOLO
import supervision as sv

from train import map_yolo_to_label


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


def draw_boxes(frame, detections, box_annotator):
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

    frame = box_annotator.annotate(labels=labels, scene=frame, detections=detections)

    return labels, frame


def run_detection():
    """
    Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
    """
    args = parse_args()
    frame_width, frame_height = args.webcam_resolutions

    # 1. Khởi tạo mô hình YOLO và BoxAnnotator
    model = YOLO("yolov8l.pt")
    box_annatator = sv.BoxAnnotator(thickness=2)
    lables_annatator = sv.LabelAnnotator(text_thickness=4, text_scale=1)

    # 2. Mở webcam và thiết lập các thông số
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # 3. Vòng lặp chính để đọc khung hình từ webcam
    while True:
        ret, frame = cap.read()
        # if not ret:
        #     print("Không nhận được khung hình (frame). Kết nối có thể đã bị ngắt.")
        #     break
        detections = detect_objects(frame, model)

        for class_name, confidence in detections:
            class_name = detections["class_name"]
            waste_label = map_yolo_to_label.map_yolo_to_label(class_name)

            if waste_label != -1:
                print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")

        frame = draw_boxes(frame, detections, box_annatator)

        # 6. Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        if cv2.waitKey(30) == 27:
            break

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


# def generate_stream(stream_url):
#     """
#     Hàm chính để thực hiện nhận diện trên webcam và hiển thị kết quả.
#     """
#     args = parse_args()
#     frame_width, frame_height = args.webcam_resolutions

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
#     model, box_annatator, lables_annatator = initialize_yolo_and_annotators(
#         "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"
#     )

#     # Mở luồng video
#     cap = initialize_video_stream(stream_url, frame_width, frame_height)

#     input_queue = Queue(maxsize=5)  # Hàng đợi để lưu khung hình đầu vào
#     output_queue = Queue(maxsize=5)  # Hàng đợi để lưu kết quả đầu ra

#     yolo_worker = YOLOWorker(model, input_queue, output_queue)
#     yolo_worker.start()

#     try:
#         while not state.terminate_flag:
#             if state.terminate_flag:  # Kiểm tra cờ dừng
#                 break

#             frame = cap.read()

#             if frame is None:
#                 print("Không nhận được khung hình.")
#                 break

#             if not input_queue.full():
#                 input_queue.put(frame)

#             # Xử lý nhận diện với YOLO
#             if not output_queue.empty():
#                 detections, annotated_frame, inference_time = output_queue.get()

#                 # Gửi nhãn đến phần cứng qua API
#                 # for class_name, confidence in zip(
#                 #     detections["class_name"], detections.confidence
#                 # ):
#                 #     waste_label = map_yolo_to_label.map_yolo_to_label(class_name)
#                 #     if waste_label != -1:
#                 #         print(f"Nhận diện: {class_name}, Nhãn phân loại: {waste_label}")
#                 #         send_to_hardware_api(waste_label)

#                 # Vẽ kết quả lên khung hình
#                 annotated_frame = box_annatator.annotate(frame, detections)

#                 video_writer = state.get_video_writer()
#                 if video_writer is not None:
#                     video_writer.write(annotated_frame)

#                 # Mã hóa khung hình sang JPEG
#                 _, buffer = cv2.imencode(".jpg", annotated_frame)
#                 frame_bytes = buffer.tobytes()

#                 # Truyền dữ liệu MJPEG
#                 yield (
#                     b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
#                 )

#             if (
#                 cv2.waitKey(1) == 27 or state.terminate_flag
#             ):  # Exit when ESC key is pressed or terminate flag is set
#                 break

#     finally:
#         cap.stop()
#         yolo_worker.stop()
#         yolo_worker.join()
#         video_writer = state.get_video_writer()
#         if video_writer:
#             video_writer.release()
#         state.set_video_writer(None)
#         state.completed_event.set()  # Báo hiệu đã hoàn tất


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
    run_detection()
