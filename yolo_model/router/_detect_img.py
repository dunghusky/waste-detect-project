import os
from typing import Union
import uuid
from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import JSONResponse


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

            img_url_s3 = _img_detect.detect_image(temp_file_path, path_model, _constants.IMG_PATH, conf, iou)

            # Xóa file tạm sau khi upload
            os.remove(temp_file_path)

        # Trả về kết quả
        return JSONResponse(
            content={
                "status": 200,
                "message": "Dự đoán hình ảnh thành công.",
                "data": img_url_s3,
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": f"Lỗi hệ thống: {str(e)}"},
            status_code=500,
        )
