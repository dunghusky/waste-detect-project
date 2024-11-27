from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import uvicorn

from yolo_model.controllers import _stream_detect
from yolo_model.manage.StateManager import state

router = APIRouter(
    prefix="/api/v1/stream",
    tags=["stream"],
)

# ----------------------------------------------------------#
# size : 800x600
@router.get("/video_feed")
def video_feed():
    try:
        # state.reset()
        stream_url = "rtmp://45.90.223.138:1256/live"  # Thay bằng stream URL thực tế: https://9500-116-105-216-200.ngrok-free.app/1
        return StreamingResponse(
            _stream_detect.generate_stream(stream_url),
            media_type="multipart/x-mixed-replace; boundary=frame",
            status_code = 200
        )
    except Exception as e:
        return JSONResponse({"status": 500, "message": "Lỗi hệ thống!"})


@router.post("/stop",)
def stop():
    try:
        state.terminate_flag = True

        # Đợi `generate_stream` hoàn tất
        state.completed_event.wait()  # Chờ tín hiệu từ generate_stream
        if not state.completed_event.is_set():
            return JSONResponse(
                {"status": 500, "message": "Timeout: Video chưa hoàn tất."}
            )

        # Truy cập file video sau khi hoàn tất
        with state.lock:
            if state.output_file:
                return FileResponse(
                    state.output_file, media_type="video/mp4", filename="output.mp4"
                )
            else:
                return JSONResponse(
                    {"status": 400, "message": "Không tìm thấy file video."}
                )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống: {str(e)}"})

    finally:
        # Đảm bảo giải phóng tài nguyên
        state.reset()
