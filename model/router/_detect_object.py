from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import uvicorn

from model.controllers import _stream_detect
from manage.StateManager import state
router = APIRouter(
    prefix="/api/v1/stream",
    tags=["stream"],
)

# ----------------------------------------------------------#
@router.get("/video_feed")
def video_feed():
    try:
        state.reset()
        stream_url = "rtmp://82.180.160.47:1888/live"  # Thay bằng stream URL thực tế
        return StreamingResponse(
            _stream_detect.generate_stream(stream_url),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": "Lỗi hệ thống!"})


@router.post("/stop",)
def stop():
    try:
        state.terminate_flag = True
        if state.video_writer is not None:
            state.video_writer.release()
            state.video_writer = None

        if state.output_file:
            return FileResponse(
                state.output_file, media_type="video/mp4", filename=state.output_file
            )
        else:
            return JSONResponse(
                {"status": 400, "message": "Không tìm thấy file video."}
            )
    except Exception as e:
        return JSONResponse({"status": 500, "message": "Lỗi hệ thống: " + +str(e)})
