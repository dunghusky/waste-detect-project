from database.dependencies.dependencies import get_db
from datetime import datetime
from database.models.Camera import Camera
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac


def save_video_process_db(
    file_name, cloudfront_url, start_time, end_time, video_duration
):
    """Lưu video vào cơ sở dữ liệu"""
    try:
        # Chuyển đổi datetime thành chuỗi
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(end_time, datetime):
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Đảm bảo video_duration là chuỗi nếu cần
        if isinstance(video_duration, float):
            video_duration = str(video_duration)
    
        # print("\n\nbbbbbbbbbbbbbbbbb")
        # print(type(file_name))
        # print("\nfile name: ", file_name)
        # print(type(cloudfront_url))
        # print("\ncloudfront_url: ", cloudfront_url)
        # print(type(start_time))
        # print("\nstart_time: ", start_time)
        # print(type(end_time))
        # print("\nend_time: ", end_time)
        # print(type(video_duration))
        # print("\nvideo_duration: ", video_duration)
        with next(get_db()) as db:
            db_session = next(get_db())
            print(f"\nDatabase session: {db_session}")
            
            new_record = VideoXuLy(
                tenVideo=file_name,  # Lưu đường dẫn video
                thoiLuong=video_duration,  # Thời gian quay video
                ngayBatDauQuay=start_time,  # Ngày bắt đầu quay
                ngayKetThuc=end_time,  # Ngày kết thúc quay
                moTa="null",  # Giả sử bạn không cần mô tả
                duongDan=cloudfront_url,  # Đường dẫn video (CloudFront)
                maCamera=1,
                maMoHinh=1,
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return new_record.maVideo  # Trả về ID của video
    except Exception as e:
        import traceback
        traceback.print_exc() 
        print(f"Lỗi ghi vào DB: {e}")


def save_details_wastes_process_db(id_video, id_waste, quantity_process):
    try:
        with next(get_db()) as db:
            save_quantity_db = ChiTietXuLyRac(
                maVideo=id_video, maRacThai=id_waste, SoLuongXuLy=quantity_process
            )
            db.add(save_quantity_db)
            db.commit()
            print("Dữ liệu ghi vào db thành công")
    except Exception as e:
        print("Lỗi ghi vào DB: " + e)
