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

from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)


@router.get("/waste_data")
def get_waste_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng ChiTietXuLyRac
        query = text(
            """
            SELECT r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, 
                d.tenDanhMuc, SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy, r.ghiChu
            FROM RacThai r
            JOIN DanhMucPhanLoaiRac d ON r.maDanhMuc = d.maDanhMuc
            LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
            GROUP BY r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, d.tenDanhMuc, r.ghiChu
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
                "tongSoLuongDaXuLy": row.tongSoLuongDaXuLy or 0,
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
        return JSONResponse({"status": 500, "message": "Lỗi hệ thống!"})
