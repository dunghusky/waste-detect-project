from datetime import datetime
import os
import _constants


def create_video():
    output_dir = _constants.VIDEO_PATH
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

    # Tạo tên file với đường dẫn đầy đủ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"output_{timestamp}.mp4")
    return output_file