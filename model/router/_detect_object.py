from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import uvicorn

from model.controllers import _stream_detect

router = APIRouter(
    prefix="/api/v1/stream",
    tags=["stream"],
)


# ----------------------------------------------------------#
@router.get("/video_feed")
def video_feed():
    stream_url = "rtmp://82.180.160.47:1888/live"  # Thay bằng stream URL thực tế
    return StreamingResponse(
        _stream_detect.generate_stream(stream_url),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
