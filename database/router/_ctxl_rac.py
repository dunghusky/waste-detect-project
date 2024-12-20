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
    prefix="/api/v1/details_process_video",
    tags=["details_process_video"],
)


@router.get("/video_detail_process_data")  # chưa test
def get_video_detail_process_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng ChiTietXuLyRac
        query = text(
            """
            SELECT c.maVideo, c.maRacThai, c.soLuongXuLy, c.ghiChu, r.tenRacThai, v.tenVideo
            FROM ChiTietXuLyRac c
            LEFT JOIN RacThai r ON c.maRacThai = r.maRacThai
            LEFT JOIN VideoXuLy v ON c.maVideo = v.maVideo
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenVideo": row.tenVideo,
                "tenRacThai": row.tenRacThai,
                "soLuongXuLy": row.soLuongXuLy,
                "ghiChu": row.ghiChu,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách CTXLR thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})
