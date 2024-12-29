from typing import Optional
from fastapi import APIRouter, Depends, Form
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

router = APIRouter(
    prefix="/api/v1/model-category",
    tags=["model-category"],
)


@router.post("/add_model_category")
def add_model_category(
    modelName: str = Form(...),
    note: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        # Thêm dữ liệu vào bảng RacThai
        new_model = DanhMucMoHinh(
            tenMoHinh=modelName,
            duongDan=link,
            ghiChu=note,
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
def update_model_category_data(
    id_model: int = Form(...),
    modelName: str = Form(None),
    note: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
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
                },
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
