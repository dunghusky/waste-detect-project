from database.dependencies.dependencies import get_db
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.RacThai import RacThai


def get_id_waste_from_class_name(class_name):
    """Truy vấn maRacThai từ bảng RacThai dựa trên maRacThaiQuyChieu."""
    try:
        with next(get_db()) as db:
            result = (
                db.query(RacThai.maRacThai)
                .filter_by(maRacThaiQuyChieu=class_name)
                .first()
            )
            if result:
                return result[0]
            return None
    except Exception as e:
        print("Lỗi truy vấn maRacThai:", str(e))
        return None
