import asyncio
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from loguru import logger
import uvicorn

from yolo_model.controllers import _stream_detect, _upload_video_s3, _save_to_db
from yolo_model.manage.StateManager import state
from yolo_model.schemas._waste_label import WasteLabel
from config import _constants, _create_file

router = APIRouter(
    prefix="/api/v1/stream",
    tags=["stream"],
)

received_labels = []
# Global storage for video URL
video_url_storage = None
# ----------------------------------------------------------#
# size : 800x600
@router.get("/video_feed")
def video_feed():
    try:
        state.start_time = datetime.now()

        stream_url = "rtmp://45.90.223.138:1256/live"  # Thay bằng stream URL thực tế: https://9500-116-105-216-200.ngrok-free.app/1
        return StreamingResponse(
            _stream_detect.generate_stream(stream_url),
            media_type="multipart/x-mixed-replace; boundary=frame",
            status_code=200,
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

        with state.lock:
            if state.output_file:
                # Lấy thời gian quay video
                start_time = state.start_time

                state.end_time = datetime.now()

                video_duration = (state.end_time - start_time).total_seconds()

                file_name = _create_file.return_file_name(state.output_file)

                logger.info(f"File video được tạo: {state.output_file}")
                print(f"\n\nLink: {state.output_file}")

                converted_video_file = _upload_video_s3.convert_video_to_mp4(state.output_file)
                state.output_file = converted_video_file  # Cập nhật lại state.output_file

                # Đảm bảo video đã chuyển đổi xong
                if not state.output_file or not os.path.exists(state.output_file):
                    return JSONResponse(
                        {
                            "status": 500,
                            "message": "Không tìm thấy video đã chuyển đổi.",
                        }
                    )

                video_url = _upload_video_s3.upload_video_to_s3(state.output_file)
                print("\nVideo: ", video_url)

                # Thay đổi URL từ S3 URL sang CloudFront URL
                # cloudfront_base_url = _constants.CLOUDFRONT_BASE_URL
                # video_file_key = video_url.split("/")[-1]  # Lấy tên file từ S3 URL
                # cloudfront_url = f"{cloudfront_base_url}{video_file_key}"
                cloudfront_url = _upload_video_s3.convert_cloudfront_link(video_url)
                print("\nVideo: ", cloudfront_url)

                global video_url_storage
                video_url_storage = cloudfront_url

                _save_to_db.save_to_db(
                   file_name, cloudfront_url, state.start_time, state.end_time, video_duration
                )

                ## Xóa các file video sau khi upload lên S3
                # if os.path.exists(state.output_file):
                #     os.remove(state.output_file)
                #     print(f"Đã xóa file video gốc: {state.output_file}")

                # converted_file = state.output_file.replace(".mp4", "_converted.mp4")
                # if os.path.exists(converted_file):
                #     os.remove(converted_file)
                #     print(f"Đã xóa file video đã chuyển đổi: {converted_file}")

                return JSONResponse(
                    content={
                        "status": 200,
                        "message": "Video uploaded successfully",
                        # "video_url": cloudfront_url,
                    },
                    status_code=200,
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


@router.post("/send-label")
async def send_label(waste_label: WasteLabel):
    received_labels.append(waste_label)
    # Xử lý gửi nhãn ở đây, ví dụ log hoặc tích hợp với phần cứng
    print(
        f"Received label: {waste_label.label}"
    )
    return {"message": "Label received successfully"}


@router.get("/get_video_url")
def get_video_url():
    try:
        global video_url_storage
        if video_url_storage:
            return JSONResponse(
                content={
                    "status": 200,
                    "message": "Lấy URL video thành công.",
                    "video_url": video_url_storage,
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                {"status": 404, "message": "Không tìm thấy video để xem."}
            )
    except Exception as e:
        return JSONResponse({"status": 500, "message": f"Lỗi hệ thống: {str(e)}"})


# @router.get("/view-labels")
# async def view_labels():
#     return {"received_labels": received_labels}
