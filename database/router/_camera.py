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
    prefix="/api/v1/camera",
    tags=["camera"],
)


@router.get("/camera_data")  # chưa test
def get_camera_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng ChiTietXuLyRac
        query = text(
            """
            SELECT * FROM Camera
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenCamera": row.tenCamera,
                "diaDiem": row.diaDiem,
                "trangThaiHoatDong": row.trangThaiHoatDong,
                "moTa": row.moTa,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách camera thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})
