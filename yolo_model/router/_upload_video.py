import uuid
import magic
from fastapi import (
    File,
    UploadFile,
    Form,
    Request,
    BackgroundTasks,
    Response,
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from typing import List, Union, Dict
from fastapi import FastAPI, APIRouter
from yolo_model.controllers import _upload_video_s3 as video_s3

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["upload"],
)

received_labels = []

@router.post("/upload-images-to-s3/")
async def upload_to_s3(
    # user_id: str = Form(...),
    # page_id: str = Form(...),
    files: Union[UploadFile, List[UploadFile]] = None,
    # current_user: dict = Depends(get_current_user),
):
    try:
        if not files or len(files) == 0:
            return JSONResponse(
                content={
                    "status": 400,
                    "message": "Không tìm thấy file",
                },
                status_code=400,
            )
        if isinstance(files, UploadFile):
            files = [files]

        file_urls = []

        for file in files:
            contents = await file.read()

            file_type = magic.from_buffer(buffer=contents, mime=True)

            file_extension = video_s3.SUPPORT_FILE_TYPES[file_type]
            if isinstance(file_extension, list):
                file_extension = file_extension[
                    0
                ]  # Lấy phần mở rộng đầu tiên trong danh sách

            file_key = f"{uuid.uuid4()}.{file_extension}"
            file_url = await video_s3.s3_upload(
                contents=contents, key=file_key, mime_type=file_type
            )
            # _mysql_mekongai.save_images_to_db(user_id, file_url)
            file_urls.append(file_url)

        return JSONResponse(
            content={
                "status": 200,
                "message": "Video uploaded successfully",
                "file_urls": file_urls,
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 400, "message": "Error: " + str(e)}, status_code=400
        )
