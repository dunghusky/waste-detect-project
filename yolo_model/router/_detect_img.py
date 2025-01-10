import os
from typing import Union
import uuid
from fastapi import APIRouter, Form, Query, UploadFile, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse


from yolo_model.controllers import _upload_s3, _img_detect
from config import _constants

router = APIRouter(
    prefix="/api/v1/image",
    tags=["image"],
)


@router.post("/image_detect")
def send_img(
    img: Union[UploadFile, None] = None,
    conf: float = Form(...),
    iou: float = Form(...),
    path_model: str = Form(...),
):
    try:
        if img:
            # Tạo thư mục tạm nếu chưa tồn tại
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Lưu file tạm
            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{img.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(img.file.read())  # Đọc file từ UploadFile

            img_url_s3, detection_json = _img_detect.detect_image(temp_file_path, path_model, _constants.IMG_PATH, conf, iou)

            # Xóa file tạm sau khi upload
            os.remove(temp_file_path)

        # Trả về kết quả
        return JSONResponse(
            content={
                "status": 200,
                "message": "Dự đoán hình ảnh thành công.",
                "data": img_url_s3,
                "detection": detection_json
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
        

@router.get("/video_stream")
def video_stream(video: str, conf: float = 0.1, iou: float = 0.5, path_model: str = Form(...)):
    if video:
            # Tạo thư mục tạm nếu chưa tồn tại
            temp_dir = "./file_path/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Lưu file tạm
            temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{video.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(video.file.read())  # Đọc file từ UploadFile

    return StreamingResponse(
        _img_detect.generate_stream_with_detection(temp_file_path, path_model, conf, iou),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@router.websocket("/json_predictions")
async def json_predictions(websocket: WebSocket, video_path: str = Query(...), model_path: str = Query(...)):
    """
    Nhận video_path và model_path từ query parameters trong WebSocket URL.
    """
    await websocket.accept()
    try:
        # Gọi hàm generate_stream_with_detection với các tham số truyền động
        await _img_detect.generate_stream_with_detection(video_path, model_path, websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
