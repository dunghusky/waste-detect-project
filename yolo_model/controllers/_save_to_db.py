from database.dependencies.dependencies import get_db
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

def save_video_process_db(file_name ,cloudfront_url, start_time, end_time, video_duration):
    """Lưu video vào cơ sở dữ liệu"""
    try:
        with next(get_db()) as db:
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
            db.refresh(new_record)  # Làm mới đối tượng để lấy ID tự động tăng
            print("Dữ liệu ghi vào db thành công")
            return new_record.maVideo  # Trả về ID của video
    except Exception as e:
        print("Lỗi ghi vào DB: "+ e)


def save_details_wastes_process_db(
    id_video, id_waste, quantity_process, note
):
    """Lưu video vào cơ sở dữ liệu"""
    try:
        with next(get_db()) as db:
            save_quantity_db = ChiTietXuLyRac(
                maVideo = id_video,
                maRacThai = id_waste,
                SoLuongXuLy = quantity_process,
                ghiChu = note
            )
            db.add(save_quantity_db)
            db.commit()
            print("Dữ liệu ghi vào db thành công")
    except Exception as e:
        print("Lỗi ghi vào DB: " + e)
