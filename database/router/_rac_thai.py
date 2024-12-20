from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._rac_thai import WasteDelete, WasteUpdate
from database.models.Camera import Camera
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

router = APIRouter(
    prefix="/api/v1/waste",
    tags=["waste"],
)


@router.get("/waste_data")
def get_waste_data(db: Session = Depends(get_db)):
    try:

        query = text(
            """
            SELECT r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, 
                d.tenDanhMuc, SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy, r.ghiChu, r.hinhAnh
            FROM RacThai r
            JOIN DanhMucPhanLoaiRac d ON r.maDanhMuc = d.maDanhMuc
            LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
            GROUP BY r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, d.tenDanhMuc, r.ghiChu, r.hinhAnh
        """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenRacThai": row.tenRacThai,
                "maRacThaiQuyChieu": row.maRacThaiQuyChieu,
                "danhMuc": row.tenDanhMuc,
                "tongSoLuongDaXuLy": int(row.tongSoLuongDaXuLy or 0),
                "hinhAnh": row.hinhAnh,
                "ghiChu": row.ghiChu,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách rác thải thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})


@router.post("/delete_waste")
def delete_waste(request: WasteDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idWaste = request.idWaste

        waste = db.query(RacThai).filter_by(maRacThai=idWaste).first()
        if not waste:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idWaste} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(waste)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idWaste} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_waste_data")
def update_waste_data(request: WasteUpdate, db: Session = Depends(get_db)):
    try:
        data = request.dataWaste
        
        id_waste = data.get("maRacThai")
        if not id_waste:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã rác thải để cập nhật."},
                status_code=400,
            )

        # Kiểm tra rác thải có tồn tại không
        waste = db.query(RacThai).filter_by(maRacThai=id_waste).first()
        if not waste:
            return JSONResponse(
                content={"status": 404, "message": "Rác thải không tồn tại."},
                status_code=404,
            )

        # Ánh xạ tên danh mục sang mã danh mục
        category_name = data.get("tenDanhMuc")
        if category_name:
            danh_muc = (
                db.query(DanhMucPhanLoaiRac).filter_by(tenDanhMuc=category_name).first()
            )
            if not danh_muc:
                return JSONResponse(
                    content={
                        "status": 404,
                        "message": f"Danh mục '{category_name}' không tồn tại.",
                    },
                    status_code=404,
                )
            waste.maDanhMuc = danh_muc.maDanhMuc

        # Cập nhật các trường khác
        if "tenRacThai" in data:
            waste.tenRacThai = data["tenRacThai"]
        if "maRacThaiQuyChieu" in data:
            waste.maRacThaiQuyChieu = data["maRacThaiQuyChieu"]
        if "ghiChu" in data:
            waste.ghiChu = data["ghiChu"]
        if "hinhAnh" in data:
            waste.hinhAnh = data["hinhAnh"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật thông tin rác thải thành công.",
                "data": {
                    "maRacThai": waste.maRacThai,
                    "tenRacThai": waste.tenRacThai,
                    "maRacThaiQuyChieu": waste.maRacThaiQuyChieu,
                    "ghiChu": waste.ghiChu,
                    "maDanhMuc": waste.maDanhMuc,
                    "tenDanhMuc": category_name,
                    "hinhAnh": waste.hinhAnh,
                },
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
