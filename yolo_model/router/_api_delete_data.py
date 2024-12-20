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
    prefix="/api/v1/delete-data",
    tags=["delete-data"],
)


@router.post("/delete_model_category/{maMoHinh}")
def delete_model_category(maMoHinh: int, db: Session = Depends(get_db)):
    """
    API xóa một dòng trong bảng DanhMucMoHinh.
    Nếu có các dữ liệu liên quan trong bảng VideoXuLy, chúng sẽ bị xóa tự động nhờ CASCADE DELETE.
    """
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        model_category = db.query(DanhMucMoHinh).filter_by(maMoHinh=maMoHinh).first()
        if not model_category:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã mô hình {maMoHinh} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(model_category)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã mô hình {maMoHinh} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
