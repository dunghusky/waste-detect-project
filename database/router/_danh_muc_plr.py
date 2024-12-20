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
    prefix="/api/v1/waste-category",
    tags=["waste-category"],
)


@router.get("/waste_category_data") 
def get_waste_category_data(db: Session = Depends(get_db)):
    try:
        
        query = text(
            """
            SELECT d.maDanhMuc, d.tenDanhMuc, d.maDanhMucQuyChieu, d.ghiChu,
                SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy, d.hinhAnh
            FROM DanhMucPhanLoaiRac d
            LEFT JOIN RacThai r ON d.maDanhMuc = r.maDanhMuc
            LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
            GROUP BY d.maDanhMuc, d.tenDanhMuc, d.maDanhMucQuyChieu, d.ghiChu
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenDanhMuc": row.tenDanhMuc,
                "maDanhMucQuyChieu": row.maDanhMucQuyChieu,
                "tongSoLuongDaXuLy": int(row.tongSoLuongDaXuLy or 0),
                "hinhAnh": row.hinhAnh,
                "ghiChu": row.ghiChu,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách danh mục rác thải thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})
