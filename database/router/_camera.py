from typing import Optional
from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._camera import CameraDelete, CameraUpdate
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


@router.post("/add_camera")
def add_camera(
    cameraName: str = Form(...),
    note: Optional[str] = Form(None),
    isStatus: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        if isStatus:
            status_value = int(isStatus)
        else:
            status_value = 1
        # Thêm dữ liệu vào bảng RacThai
        new_camera = Camera(
            tenCamera=cameraName,
            diaDiem=address,
            trangThaiHoatDong=status_value,
            moTa=note,
        )

        # Lưu vào database
        db.add(new_camera)
        db.commit()
        db.refresh(new_camera)

        # Trả về kết quả
        return JSONResponse(
            content={
                "status": 200,
                "message": "Thêm mới camera thành công.",
                "data": {
                    "maCamera": new_camera.maCamera,
                    "tenCamera": new_camera.tenCamera,
                    "diaDiem": new_camera.diaDiem,
                    "trangThaiHoatDong": new_camera.trangThaiHoatDong,
                    "moTa": new_camera.moTa,
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
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
                "maCamera": row.maCamera,
                "tenCamera": row.tenCamera,
                "diaDiem": row.diaDiem,
                "trangThaiHoatDong": row.trangThaiHoatDong,
                "moTa": row.moTa,
            }
            for row in result
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


@router.post("/delete_camera")
def delete_camera(request: CameraDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idCamera = request.idCamera

        camera = db.query(Camera).filter_by(maCamera=idCamera).first()
        if not camera:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idCamera} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(camera)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idCamera} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_camera_data")
def update_camera_data(request: CameraUpdate, db: Session = Depends(get_db)):
    try:
        data = request.dataCamera
        
        id_camera = data.get("maCamera")
        if not id_camera:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã camera để cập nhật."},
                status_code=400,
            )

        category = db.query(Camera).filter_by(maCamera=id_camera).first()
        if not category:
            return JSONResponse(
                content={"status": 404, "message": "Danh mục không tồn tại."},
                status_code=404,
            )

        if "tenCamera" in data:
            category.tenCamera = data["tenCamera"]
        if "diaDiem" in data:
            category.diaDiem = data["diaDiem"]
        if "trangThaiHoatDong" in data:
            category.trangThaiHoatDong = data["trangThaiHoatDong"]
        if "moTa" in data:
            category.moTa = data["moTa"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật camera thành công.",
                "data": {
                    "maCamera": category.maCamera,
                    "tenCamera": category.tenCamera,
                    "diaDiem": category.diaDiem,
                    "moTa": category.moTa,
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
