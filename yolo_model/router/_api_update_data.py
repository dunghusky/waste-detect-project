import asyncio
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from loguru import logger
import uvicorn

from yolo_model.controllers import (
    _stream_detect,
    _upload_video_s3,
    _save_to_db,
    _trigger_to_db,
)
from yolo_model.manage.StateManager import state
from yolo_model.schemas._waste_label import WasteLabel
from config import _constants, _create_file
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
    prefix="/api/v1/update-data",
    tags=["update-data"],
)


@router.post("/update_waste_category_data")  # chưa test
def update_waste_category_data(data: dict, db: Session = Depends(get_db)):
    try:
        # Lấy thông tin mã danh mục từ dữ liệu gửi lên
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

@router.post("/update_model_category_data")       
def update_model_category_data(data: dict, db: Session = Depends(get_db)):
    try:
        id_model_category = data.get("maMoHinh")
        if not id_model_category:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã mô hình để cập nhật."},
                status_code=400,
            )

        category = (db.query(DanhMucMoHinh).filter_by(maMoHinh = id_model_category).first())
        if not category:
            return JSONResponse(
                content={"status": 404, "message": "Danh mục không tồn tại."},
                status_code=404,
            )

        if "tenMoHinh" in data:
            category.tenMoHinh = data["tenMoHinh"]
        if "duongDan" in data:
            category.duongDan = data["duongDan"]
        if "ghiChu" in data:
            category.ghiChu = data["ghiChu"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật danh mục mô hình thành công.",
                "data": {
                    "maMoHinh": category.maMoHinh,
                    "tenMoHinh": category.tenMoHinh,
                    "duongDan": category.duongDan,
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


@router.post("/update_camera_data")
def update_camera_data(data: dict, db: Session = Depends(get_db)):
    try:
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


@router.post("/update_waste_data")
def update_waste_data(data: dict, db: Session = Depends(get_db)):
    try:
        # Lấy mã rác thải từ dữ liệu gửi lên
        id_waste = data.get("maRacThai")
        if not id_waste:
            return JSONResponse(
                content={
                    "status": 400,
                    "message": "Thiếu mã rác thải để cập nhật."
                },
                status_code=400
            )

        # Kiểm tra rác thải có tồn tại không
        waste = db.query(RacThai).filter_by(maRacThai=id_waste).first()
        if not waste:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "Rác thải không tồn tại."
                },
                status_code=404
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
            content={
                "status": 500,
                "message": f"Lỗi hệ thống: {str(e)}"
            },
            status_code=500
        )


@router.post("/update_process_video_data")
def update_process_video_data(data: dict, db: Session = Depends(get_db)):
    try:
        id_video = data.get("maVideo")
        if not id_video:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã video để cập nhật."},
                status_code=400,
            )

        video = db.query(VideoXuLy).filter_by(maVideo=id_video).first()
        if not video:
            return JSONResponse(
                content={"status": 404, "message": "Video không tồn tại."},
                status_code=404,
            )

        if "moTa" in data:
            video.moTa = data["moTa"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật mô tả thành công.",
                "data": {
                    "moTa": video.moTa,
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_details_wastes_data")
def update_details_wastes_data(data: dict, db: Session = Depends(get_db)):
    try:
        id_video = data.get("maVideo")
        id_waste = data.get("maRacThai")

        if not id_video or not id_waste:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã để cập nhật."},
                status_code=400,
            )

        process = db.query(ChiTietXuLyRac).filter_by(maVideo=id_video, maRacThai=id_waste).first()
        if not process:
            return JSONResponse(
                content={"status": 404, "message": "Bảng không tồn tại."},
                status_code=404,
            )

        if "ghiChu" in data:
            process.ghiChu = data["ghiChu"]

        # Ghi cập nhật vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật mô tả thành công.",
                "data": {
                    "ghiChu": process.ghiChu,
                },
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
