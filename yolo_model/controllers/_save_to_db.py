import asyncio
from database.dependencies.dependencies import get_db
from database.models.VideoXuLy import VideoXuLy

def save_to_db(file_name ,cloudfront_url, start_time, end_time, video_duration):
    """Lưu video vào cơ sở dữ liệu"""
    try:
        with next(get_db()) as db:
            save_db = VideoXuLy(
                tenVideo=file_name,  # Lưu đường dẫn video
                thoiLuong=video_duration,  # Thời gian quay video
                ngayBatDauQuay=start_time,  # Ngày bắt đầu quay
                ngayKetThuc=end_time,  # Ngày kết thúc quay
                moTa="null",  # Giả sử bạn không cần mô tả
                duongDan=cloudfront_url,  # Đường dẫn video (CloudFront)
                maCamera=1,
                maMoHinh=1,
            )
            db.add(save_db)
            db.commit()
            print("Dữ liệu ghi vào db thành công")
    except Exception as e:
        print("Lỗi ghi vào DB: "+ e)
