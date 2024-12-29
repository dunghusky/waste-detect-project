from typing import Optional
from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._video_xu_ly import VideoDelete, VideoUpdate
from database.models.Camera import Camera
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

router = APIRouter(
    prefix="/api/v1/process_video",
    tags=["process_video"],
)


@router.get("/video_process_data")
def get_video_process_data(db: Session = Depends(get_db)):
    try:
        # Truy vấn tính tổng từ bảng VideoXuLy
        query = text(
            """
            SELECT v.maVideo, v.tenVideo, v.thoiLuong, v.ngayBatDauQuay, v.ngayKetThuc,
                v.moTa, v.duongDan, c.tenCamera, m.tenMoHinh, c.maCamera, m.maMoHinh
            FROM VideoXuLy v
            LEFT JOIN Camera c ON v.maCamera = c.maCamera
            LEFT JOIN DanhMucMoHinh m ON v.maMoHinh = m.maMoHinh
            """
        )

        result = db.execute(query)

        # Xử lý kết quả
        data = [
            {
                "maVideo": row.maVideo,
                "maCamera": row.maCamera,
                "maMoHinh": row.maMoHinh,
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
            for row in result
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


@router.post("/delete_video")
def delete_video(request: VideoDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idVideo = request.idVideo

        video = db.query(VideoXuLy).filter_by(maVideo=idVideo).first()
        if not video:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idVideo} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(video)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idVideo} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_process_video_data")
def update_process_video_data(
    id_video: int = Form(...),
    note: Optional[str] = Form(None),
    db: Session = Depends(get_db)):
    try:
        # Tìm rác thải dựa trên ID
        video = db.query(VideoXuLy).filter_by(maVideo=id_video).first()
        if not video:
            return JSONResponse(
                content={"status": 404, "message": "Rác thải không tồn tại."},
                status_code=404,
            )
        if note:
            video.moTa = note

        # Lưu thay đổi vào database
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": "Cập nhật thông tin rác thải thành công.",
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
