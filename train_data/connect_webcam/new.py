import cv2

def main():
    # GStreamer pipeline mới cho RTMP với cấu hình tối ưu
    gst_pipeline = (
        "rtspsrc location=rtmp://54.92.211.110:1935/live latency=0 ! "
        "decodebin ! videoconvert ! appsink drop=true sync=false"
    )

    # Khởi tạo VideoCapture với GStreamer Pipeline
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Kiểm tra xem việc mở luồng RTMP có thành công không
    if not cap.isOpened():
        print(f"Không thể mở luồng video từ GStreamer pipeline")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không nhận được khung hình (frame). Kết nối có thể đã bị ngắt.")
            break

        # Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream with GStreamer", frame)

        # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        if cv2.waitKey(1) == 27:
            break

    # Giải phóng tài nguyên sau khi kết thúc
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
