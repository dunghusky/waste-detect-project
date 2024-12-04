import asyncio
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from loguru import logger
import uvicorn

from yolo_model.controllers import _stream_detect, _upload_video_s3
from yolo_model.manage.StateManager import state
from yolo_model.schemas._waste_label import WasteLabel
from config import _constants

router = APIRouter(
    prefix="/api/v1/stream",
    tags=["stream"],
)

received_labels = []
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
                logger.info(f"File video được tạo: {state.output_file}")
                print(f"\n\nLink: {state.output_file}")

                video_url = _upload_video_s3.upload_video_to_s3(state.output_file)

                video_url = asyncio.get_event_loop().run_until_complete(video_url)
                print("\nVideo: ", video_url)

                # Thay đổi URL từ S3 URL sang CloudFront URL
                cloudfront_base_url = _constants.CLOUDFRONT_BASE_URL
                video_file_key = video_url.split("/")[-1]  # Lấy tên file từ S3 URL
                cloudfront_url = f"{cloudfront_base_url}{video_file_key}"

                print("\nVideo: ", cloudfront_url)

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
                        "video_url": cloudfront_url,
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


@router.get("/view-video")
async def view_video():
    try:
        # Trả về URL của video vừa ghi và upload lên S3
        if state.output_file:
            video_url = f"https://{_upload_video_s3.AWS_BUCKET}.s3.{_upload_video_s3.AWS_REGION}.amazonaws.com/videos/{os.path.basename(state.output_file)}"
            return JSONResponse(
                content={
                    "status": 200,
                    "message": "Video URL retrieved successfully",
                    "video_url": video_url,
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={"status": 400, "message": "Không tìm thấy video."},
                status_code=400,
            )
    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )


# @router.get("/view-labels")
# async def view_labels():
#     return {"received_labels": received_labels}
