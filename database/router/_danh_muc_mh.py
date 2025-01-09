from datetime import datetime
import os
from typing import Optional, Union
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._danh_muc_mh import CategoryModelDelete, CategoryModelUpdate
from database.models.Camera import Camera
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac
from yolo_model.controllers import _upload_s3

router = APIRouter(
    prefix="/api/v1/model-category",
    tags=["model-category"],
)


@router.post("/add_model_category")
@router.post("/add_model_category/")
def add_model_category(
    modelName: str = Form(...),
    note: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    img: Union[UploadFile, None] = None,
    date: Optional[str] = Form(None),
    results: Union[UploadFile, None] = None,
    db: Session = Depends(get_db),
):
    try:
        print(f"modelName: {modelName}")
        print(f"note: {note}")
        print(f"link: {link}")
        print(f"date: {date}")

        if img:
            print(f"IMG Info: filename={img.filename}, content_type={img.content_type}")

        if results:
            print(f"RESULTS Info: filename={results.filename}, content_type={results.content_type}")

        dmy_date = datetime.strptime(date, "%d-%m-%Y").date() if date else datetime.utcnow().date()

        img_url = None
        if img:
            # Tạo thư mục tạm nếu chưa tồn tại
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Lưu file tạm
            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{img.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(img.file.read())  # Đọc file từ UploadFile

            # Gọi hàm upload_file_to_s3 với đường dẫn file tạm
            link_img = _upload_s3.upload_file_to_s3(temp_file_path)
            
            img_url = _upload_s3.convert_cloudfront_link(link_img)

            # Xóa file tạm sau khi upload
            os.remove(temp_file_path)
            
        results_url = None
        if results:
            # Tạo thư mục tạm nếu chưa tồn tại
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Lưu file tạm
            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{results.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(results.file.read())  # Đọc file từ UploadFile

            # Gọi hàm upload_file_to_s3 với đường dẫn file tạm
            link_results = _upload_s3.upload_file_to_s3(temp_file_path)
            
            results_url = _upload_s3.convert_cloudfront_link(link_results)
            
            # Xóa file tạm sau khi upload
            os.remove(temp_file_path)
            
        # Thêm dữ liệu vào bảng RacThai
        new_model = DanhMucMoHinh(
            tenMoHinh=modelName,
            duongDan=link,
            ghiChu=note,
            ketQuaTrain=results_url,
            hinhAnh=img_url,
            ngayThem=dmy_date
        )

        # Lưu vào database
        db.add(new_model)
        db.commit()
        db.refresh(new_model)

        # Trả về kết quả
        return JSONResponse(
            content={
                "status": 200,
                "message": "Thêm mới mô hình thành công.",
                "data": {
                    "maMoHinh": new_model.maMoHinh,
                    "tenMoHinh": new_model.tenMoHinh,
                    "duongDan": new_model.duongDan,
                    "ghiChu": new_model.ghiChu,
                    "ketQua": new_model.ketQuaTrain,
                    "img": new_model.hinhAnh,
                    "ngayThem": new_model.ngayThem.strftime("%d-%m-%Y")
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.get("/model_category_data")  # chưa test
@router.get("/model_category_data/")  # chưa test
def get_model_category_data(db: Session = Depends(get_db)):
    try:
        query = text(
            """
            SELECT * FROM DanhMucMoHinh
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "maMoHinh": row.maMoHinh,
                "tenMoHinh": row.tenMoHinh,
                "duongDan": row.duongDan,
                "ghiChu": row.ghiChu,
                "ketQua": row.ketQuaTrain,
                "img": row.hinhAnh,
                "ngayThem": (
                    row.ngayThem.strftime("%d-%m-%Y")
                    if row.ngayThem
                    else None
                )
            }
            for row in result
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách danh mục mô hình thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})


@router.post("/delete_model_category")
@router.post("/delete_model_category/")
def delete_model_category(request: CategoryModelDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idModel = request.idModel

        model = db.query(DanhMucMoHinh).filter_by(maMoHinh=idModel).first()
        if not model:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idModel} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(model)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idModel} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_model_category_data")
@router.post("/update_model_category_data/")
def update_model_category_data(
    id_model: int = Form(...),
    modelName: str = Form(None),
    note: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    img: Union[UploadFile, None] = None,
    date: Optional[str] = Form(None),
    results: Union[UploadFile, None] = None,
    db: Session = Depends(get_db),
):
    try:
        # Tìm rác thải dựa trên ID
        model = db.query(DanhMucMoHinh).filter_by(maMoHinh=id_model).first()
        if not model:
            return JSONResponse(
                content={"status": 404, "message": "Rác thải không tồn tại."},
                status_code=404,
            )
        
        # Cập nhật hình ảnh nếu có
        if img:
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{img.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(img.file.read())

            try:
                link_img = _upload_s3.upload_file_to_s3(temp_file_path)
                img_url = _upload_s3.convert_cloudfront_link(link_img)
                model.hinhAnh = img_url
            finally:
                os.remove(temp_file_path)
        
        # Cập nhật hình ảnh nếu có
        if results:
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{results.filename}"
            file_content = results.file.read()

            if not file_content:
                return JSONResponse(
                    content={"status": 400, "message": "File kết quả tải lên bị trống."},
                    status_code=400,
                )

            with open(temp_file_path, "wb") as f:
                f.write(file_content)
                
            try:
                link_results = _upload_s3.upload_file_to_s3(temp_file_path)
                results_url = _upload_s3.convert_cloudfront_link(link_results)
                model.ketQuaTrain = results_url
            finally:
                os.remove(temp_file_path)
        else:
            # Bỏ qua cập nhật trường results nếu không có file
            print("Không cập nhật trường results vì không có file được gửi.")

        if date:
            try:
                dmy_date = datetime.strptime(date, "%d-%m-%Y").date()
                model.ngayThem = dmy_date
            except ValueError:
                return JSONResponse(
                    content={"status": 400, "message": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng DD-MM-YYYY."},
                    status_code=400,
                )
        # Cập nhật các trường khác nếu có
        if modelName:
            model.tenMoHinh = modelName
        if note:
            model.ghiChu = note
        if link:
            model.duongDan = link

        # Lưu thay đổi vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật thông tin rác thải thành công.",
                "data": {
                    "maMoHinh": model.maMoHinh,
                    "tenMoHinh": model.tenMoHinh,
                    "duongDan": model.duongDan,
                    "ghiChu": model.ghiChu,
                    "ketQua": model.ketQuaTrain,
                    "img": model.hinhAnh,
                    "ngayThem": (
                        model.ngayThem.strftime("%d-%m-%Y")
                        if model.ngayThem
                        else None
                    )
                },
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
