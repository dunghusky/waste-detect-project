from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._danh_muc_plr import CategoryWasteDelete, CategoryWasteUpdate
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


@router.post("/delete_waste_category")
def delete_waste_category(request: CategoryWasteDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idWasteC = request.idModel

        category = db.query(DanhMucPhanLoaiRac).filter_by(maDanhMuc=idWasteC).first()
        if not category:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idWasteC} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(category)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idWasteC} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_waste_category_data")  # chưa test
def update_waste_category_data(
    request: CategoryWasteUpdate, db: Session = Depends(get_db)
):
    try:
        data = request.dataCategoryWaste
        
        id_waste_category = data.get("maDanhMuc")
        if not id_waste_category:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã danh mục để cập nhật."},
                status_code=400,
            )

        # Kiểm tra danh mục có tồn tại không
        category = (
            db.query(DanhMucPhanLoaiRac).filter_by(maDanhMuc=id_waste_category).first()
        )
        if not category:
            return JSONResponse(
                content={"status": 404, "message": "Danh mục không tồn tại."},
                status_code=404,
            )

        # Cập nhật các trường
        if "tenDanhMuc" in data:
            category.tenDanhMuc = data["tenDanhMuc"]
        if "maDanhMucQuyChieu" in data:
            category.maDanhMucQuyChieu = data["maDanhMucQuyChieu"]
        if "ghiChu" in data:
            category.ghiChu = data["ghiChu"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật danh mục rác thải thành công.",
                "data": {
                    "maDanhMuc": category.maDanhMuc,
                    "tenDanhMuc": category.tenDanhMuc,
                    "maDanhMucQuyChieu": category.maDanhMucQuyChieu,
                    "ghiChu": category.ghiChu,
                },
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
