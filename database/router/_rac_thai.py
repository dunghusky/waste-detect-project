import os
from typing import Optional, Union
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile
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

from yolo_model.controllers import _upload_s3
router = APIRouter(
    prefix="/api/v1/waste",
    tags=["waste"],
)


@router.post("/add_waste")
@router.post("/add_waste/")
def add_waste(
    wasteName: str = Form(...),
    note: Optional[str] = Form(None),
    wasteId: str = Form(...),
    categoryName: str = Form(...),
    img: Union[UploadFile, None] = None,
    db: Session = Depends(get_db),
):
    try:
        img_url = None
        if img:
            # Tạo thư mục tạm nếu chưa tồn tại
            temp_dir = "/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Lưu file tạm
            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{img.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(img.file.read())  # Đọc file từ UploadFile

            # Gọi hàm upload_file_to_s3 với đường dẫn file tạm
            link_img = _upload_s3.upload_file_to_s3(temp_file_path)
            # Xóa file tạm sau khi upload
            os.remove(temp_file_path)
            img_url = _upload_s3.convert_cloudfront_link(link_img)
        # Tìm mã danh mục (maDanhMuc) dựa trên tên danh mục (categoryName)
        category = (
            db.query(DanhMucPhanLoaiRac).filter_by(tenDanhMuc=categoryName).first()
        )
        if not category:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Danh mục '{categoryName}' không tồn tại.",
                },
                status_code=404,
            )

        # Thêm dữ liệu vào bảng RacThai
        new_waste = RacThai(
            tenRacThai=wasteName,
            ghiChu=note,
            hinhAnh=img_url,
            maRacThaiQuyChieu=wasteId,
            maDanhMuc=category.maDanhMuc,
        )

        # Lưu vào database
        db.add(new_waste)
        db.commit()
        db.refresh(new_waste)

        # Trả về kết quả
        return JSONResponse(
            content={
                "status": 200,
                "message": "Thêm mới rác thải thành công.",
                "data": {
                    "maRacThai": new_waste.maRacThai,
                    "tenRacThai": new_waste.tenRacThai,
                    "maDanhMuc": category.maDanhMuc,
                    "tenDanhMuc": category.tenDanhMuc,
                    "ghiChu": new_waste.ghiChu,
                    "hinhAnh": new_waste.hinhAnh,
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.get("/waste_data")
@router.get("/waste_data/")
def get_waste_data(db: Session = Depends(get_db)):
    try:

        query = text(
            """
            SELECT r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, d.maDanhMuc,
                d.tenDanhMuc, SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy, r.ghiChu, r.hinhAnh
            FROM RacThai r
            JOIN DanhMucPhanLoaiRac d ON r.maDanhMuc = d.maDanhMuc
            LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
            GROUP BY r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, d.tenDanhMuc, r.ghiChu, r.hinhAnh, d.maDanhMuc
        """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "maRacThai": row.maRacThai,
                "maDanhMuc": row.maDanhMuc,
                "tenRacThai": row.tenRacThai,
                "maRacThaiQuyChieu": row.maRacThaiQuyChieu,
                "danhMuc": row.tenDanhMuc,
                "tongSoLuongDaXuLy": int(row.tongSoLuongDaXuLy or 0),
                "hinhAnh": row.hinhAnh,
                "ghiChu": row.ghiChu,
            }
            for row in result
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
@router.post("/delete_waste/")
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
@router.post("/update_waste_data/")
def update_waste_data(
    id_waste: int = Form(...),
    wasteName: str = Form(None),
    note: Optional[str] = Form(None),
    wasteId: str = Form(None),
    categoryName: str = Form(None),
    img: Union[UploadFile, None] = None,
    db: Session = Depends(get_db),
):
    try:
        # Tìm rác thải dựa trên ID
        waste = db.query(RacThai).filter_by(maRacThai=id_waste).first()
        if not waste:
            return JSONResponse(
                content={"status": 404, "message": "Rác thải không tồn tại."},
                status_code=404,
            )

        # Cập nhật danh mục nếu có
        if categoryName:
            category = (
                db.query(DanhMucPhanLoaiRac).filter_by(tenDanhMuc=categoryName).first()
            )
            if not category:
                return JSONResponse(
                    content={
                        "status": 404,
                        "message": f"Danh mục '{categoryName}' không tồn tại.",
                    },
                    status_code=404,
                )
            waste.maDanhMuc = category.maDanhMuc

        # Cập nhật hình ảnh nếu có
        if img:
            temp_dir = "/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{img.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(img.file.read())

            try:
                link_img = _upload_s3.upload_file_to_s3(temp_file_path)
                img_url = _upload_s3.convert_cloudfront_link(link_img)
                waste.hinhAnh = img_url
            finally:
                os.remove(temp_file_path)

        # Cập nhật các trường khác nếu có
        if wasteName:
            waste.tenRacThai = wasteName
        if note:
            waste.ghiChu = note
        if wasteId:
            waste.maRacThaiQuyChieu = wasteId

        # Lưu thay đổi vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật thông tin rác thải thành công.",
                "data": {
                    "maRacThai": waste.maRacThai,
                    "maRacThaiQuyChieu": waste.maRacThaiQuyChieu,
                    "tenRacThai": waste.tenRacThai,
                    "maDanhMuc": waste.maDanhMuc,
                    "tenDanhMuc": categoryName,
                    "ghiChu": waste.ghiChu,
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
