from database.dependencies.dependencies import get_db
from database.models.Camera import Camera
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

def save_video_process_db(file_name ,cloudfront_url, start_time, end_time, video_duration):
    """Lưu video vào cơ sở dữ liệu"""
    try:
        print("\n\nbbbbbbbbbbbbbbbbb")
        print("\nfile name: ", file_name)
        print("\ncloudfront_url: ", cloudfront_url)
        print("\nstart_time: ", start_time)
        print("\nend_time: ", end_time)
        print("\nvideo_duration: ", video_duration)
        with next(get_db()) as db:
            print("aaaaaaaaaaaaaaaa")
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
            print("\nNew reoced: ", new_record)
            db.add(new_record)
            db.commit()
            db.refresh(new_record)  # Làm mới đối tượng để lấy ID tự động tăng
            print("Dữ liệu ghi vào db thành công")
            return new_record.maVideo  # Trả về ID của video
    except Exception as e:
        print("Lỗi ghi vào DB: "+ e)


def save_details_wastes_process_db(
    id_video, id_waste, quantity_process
):
    try:
        with next(get_db()) as db:
            save_quantity_db = ChiTietXuLyRac(
                maVideo = id_video,
                maRacThai = id_waste,
                SoLuongXuLy = quantity_process
            )
            db.add(save_quantity_db)
            db.commit()
            print("Dữ liệu ghi vào db thành công")
    except Exception as e:
        print("Lỗi ghi vào DB: " + e)
