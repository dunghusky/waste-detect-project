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












