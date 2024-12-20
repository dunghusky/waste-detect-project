from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.models.Camera import Camera
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

router = APIRouter(
    prefix="/api/v1/process_video",
    tags=["process_video"],
)


@router.get("/video_process_data")
def get_video_process_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng VideoXuLy
        query = text(
            """
            SELECT v.maVideo, v.tenVideo, v.thoiLuong, v.ngayBatDauQuay, v.ngayKetThuc,
                v.moTa, v.duongDan, c.tenCamera, m.tenMoHinh
            FROM VideoXuLy v
            LEFT JOIN Camera c ON v.maCamera = c.maCamera
            LEFT JOIN DanhMucMoHinh m ON v.maMoHinh = m.maMoHinh
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenVideo": row.tenVideo,
                "thoiLuong": row.thoiLuong,
                "ngayBatDauQuay": (
                    row.ngayBatDauQuay.strftime("%Y-%m-%d %H:%M:%S")
                    if row.ngayBatDauQuay
                    else None
                ),
                "ngayKetThuc": (
                    row.ngayKetThuc.strftime("%Y-%m-%d %H:%M:%S")
                    if row.ngayKetThuc
                    else None
                ),
                "duongDan": row.duongDan,
                "tenCamera": row.tenCamera,
                "tenMoHinh": row.tenMoHinh,
                "moTa": row.moTa,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách VXL thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})
