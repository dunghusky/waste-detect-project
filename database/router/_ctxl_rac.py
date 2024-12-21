from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from database.dependencies.dependencies import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.schemas._ctxl_rac import ProcessWasteDelete, ProcessWasteUpdate
from database.models.Camera import Camera
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.RacThai import RacThai
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac

router = APIRouter(
    prefix="/api/v1/details_process_video",
    tags=["details_process_video"],
)


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
                "maVideo": row.maVideo,
                "maRacThai": row.maRacThai,
                "tenVideo": row.tenVideo,
                "tenRacThai": row.tenRacThai,
                "soLuongXuLy": row.soLuongXuLy,
                "ghiChu": row.ghiChu,
            }
            for row in result
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


@router.post("/delete_details_waste")
def delete_details_waste(request: ProcessWasteDelete, db: Session = Depends(get_db)):
    try:
        # Kiểm tra xem mã mô hình có tồn tại không
        idVideo = request.idVideo
        idWaste  = request.idWaste

        camera = (
            db.query(ChiTietXuLyRac)
            .filter_by(maVideo=idVideo, maRacThai=idWaste)
            .first()
        )
        if not camera:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Mã {idVideo} {idWaste} không tồn tại.",
                },
                status_code=404,
            )

        # Xóa dòng trong bảng DanhMucMoHinh
        db.delete(camera)
        db.commit()

        return JSONResponse(
            content={
                "status": 200,
                "message": f"Xóa mã {idVideo} {idWaste} thành công.",
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


@router.post("/update_details_wastes_data")
def update_details_wastes_data(
    request: ProcessWasteUpdate, db: Session = Depends(get_db)
):
    try:
        data = request.dataProcessWaste

        id_video = data.get("maVideo")
        id_waste = data.get("maRacThai")

        if not id_video or not id_waste:
            return JSONResponse(
                content={"status": 400, "message": "Thiếu mã để cập nhật."},
                status_code=400,
            )

        process = (
            db.query(ChiTietXuLyRac)
            .filter_by(maVideo=id_video, maRacThai=id_waste)
            .first()
        )
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
