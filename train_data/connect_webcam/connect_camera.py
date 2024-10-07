import cv2
import numpy as np


def main():
    # Thay đổi đường dẫn source thành địa chỉ RTMP của bạn
    rtmp_url = "rtmp://54.92.211.110:1915/live"

    # Khởi tạo VideoCapture với đường dẫn RTMP
    cap = cv2.VideoCapture(rtmp_url)
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

        # Hiển thị khung hình
        cv2.imshow("YOLOv8 - RTMP Stream", frame)

        # # Nhấn phím ESC (mã ASCII 27) để thoát khỏi cửa sổ
        # if cv2.waitKey(1) == 27:
        #     break

    # Giải phóng tài nguyên sau khi kết thúc
    # cap.release()
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
