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
    prefix="/api/v1/get-data",
    tags=["get-data"],
)


# @router.get("/waste_data")
# def get_waste_data(db: Session = Depends(get_db)):
#     try:

#         query = text(
#             """
#             SELECT r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, 
#                 d.tenDanhMuc, SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy, r.ghiChu
#             FROM RacThai r
#             JOIN DanhMucPhanLoaiRac d ON r.maDanhMuc = d.maDanhMuc
#             LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
#             GROUP BY r.maRacThai, r.tenRacThai, r.maRacThaiQuyChieu, d.tenDanhMuc, r.ghiChu
#         """
#         )

#         result = db.execute(query)

#         # Xử lý kết quả
#         data = [
#             {
#                 "STT": index + 1,
#                 "tenRacThai": row.tenRacThai,
#                 "maRacThaiQuyChieu": row.maRacThaiQuyChieu,
#                 "danhMuc": row.tenDanhMuc,
#                 "tongSoLuongDaXuLy": int(row.tongSoLuongDaXuLy or 0),
#                 "ghiChu": row.ghiChu,
#             }
#             for index, row in enumerate(result)
#         ]

#         return JSONResponse(
#             content={
#                 "status": 200,
#                 "message": "Lấy danh sách rác thải thành công.",
#                 "data": data,
#             },
#             status_code=200,
#         )
#     except Exception as e:
#         return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})


# @router.get("/waste_category_data") #chưa test
# def get_waste_category_data(db: Session = Depends(get_db)):
#     try:
#         # Truy vấn tính tổng từ bảng ChiTietXuLyRac
#         query = text(
#             """
#             SELECT d.maDanhMuc, d.tenDanhMuc, d.maDanhMucQuyChieu, d.ghiChu,
#                 SUM(c.soLuongXuLy) AS tongSoLuongDaXuLy
#             FROM DanhMucPhanLoaiRac d
#             LEFT JOIN RacThai r ON d.maDanhMuc = r.maDanhMuc
#             LEFT JOIN ChiTietXuLyRac c ON r.maRacThai = c.maRacThai
#             GROUP BY d.maDanhMuc, d.tenDanhMuc, d.maDanhMucQuyChieu, d.ghiChu
#             """
#         )

#         result = db.execute(query)

#         # Xử lý kết quả
#         data = [
#             {
#                 "STT": index + 1,
#                 "tenDanhMuc": row.tenDanhMuc,
#                 "maDanhMucQuyChieu": row.maDanhMucQuyChieu,
#                 "tongSoLuongDaXuLy": int(row.tongSoLuongDaXuLy or 0),
#                 "ghiChu": row.ghiChu,
#             }
#             for index, row in enumerate(result)
#         ]

#         return JSONResponse(
#             content={
#                 "status": 200,
#                 "message": "Lấy danh sách danh mục rác thải thành công.",
#                 "data": data,
#             },
#             status_code=200,
#         )
#     except Exception as e:
#         return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})


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
                "STT": index + 1,
                "tenMoHinh": row.tenMoHinh,
                "duongDan": row.duongDan,
                "ghiChu": row.ghiChu,
            }
            for index, row in enumerate(result)
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
                "STT": index + 1,
                "tenCamera": row.tenCamera,
                "diaDiem": row.diaDiem,
                "trangThaiHoatDong": row.trangThaiHoatDong,
                "moTa": row.moTa,
            }
            for index, row in enumerate(result)
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


@router.get("/video_process_data") 
def get_video_process_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng VideoXuLy
        query = text(
            """
            SELECT v.maVideo, v.tenVideo, v.thoiLuong, v.ngayBatDauQuay, v.ngayKetThuc,
                v.moTa, v.duongDan, c.tenCamera, m.tenMoHinh
            FROM VideoXuLy v
            LEFT JOIN Camera c ON v.maCamera = c.maCamera
            LEFT JOIN DanhMucMoHinh m ON v.maMoHinh = m.maMoHinh
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenVideo": row.tenVideo,
                "thoiLuong": row.thoiLuong,
                "ngayBatDauQuay": (
                    row.ngayBatDauQuay.strftime("%Y-%m-%d %H:%M:%S")
                    if row.ngayBatDauQuay
                    else None
                ),
                "ngayKetThuc": (
                    row.ngayKetThuc.strftime("%Y-%m-%d %H:%M:%S")
                    if row.ngayKetThuc
                    else None
                ),
                "duongDan": row.duongDan,
                "tenCamera": row.tenCamera,
                "tenMoHinh": row.tenMoHinh,
                "moTa": row.moTa,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách VXL thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})


@router.get("/video_detail_process_data")  # chưa test
def get_video_detail_process_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng ChiTietXuLyRac
        query = text(
            """
            SELECT c.maVideo, c.maRacThai, c.soLuongXuLy, c.ghiChu, r.tenRacThai, v.tenVideo
            FROM ChiTietXuLyRac c
            LEFT JOIN RacThai r ON c.maRacThai = r.maRacThai
            LEFT JOIN VideoXuLy v ON c.maVideo = v.maVideo
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "STT": index + 1,
                "tenVideo": row.tenVideo,
                "tenRacThai": row.tenRacThai,
                "soLuongXuLy": row.soLuongXuLy,
                "ghiChu": row.ghiChu,
            }
            for index, row in enumerate(result)
        ]

        return JSONResponse(
            content={
                "status": 200,
                "message": "Lấy danh sách CTXLR thành công.",
                "data": data,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống! + {e}"})
