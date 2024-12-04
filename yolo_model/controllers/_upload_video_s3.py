import asyncio
import subprocess
import boto3
from loguru import logger

from config import _constants
import uuid
import magic

from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")

AWS_BUCKET = _constants.AWS_BUCKET_NAME

s3 = boto3.resource("s3")
bucket = s3.Bucket(AWS_BUCKET)


async def s3_upload(contents: bytes, key: str, mime_type: str):
    """
    Upload video lên S3 và trả về URL của video.
    """
    logger.info(f"Uploading video to S3 with key: {key}")
    try:
        bucket.put_object(
            Key=key, Body=contents, ContentType=mime_type
        )
        file_url = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
        logger.info(f"Video uploaded successfully. URL: {file_url}")
        return file_url
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise


async def upload_video_to_s3_async(output_file: str):
    """
    Upload video lên S3 và trả về URL của video.
    """
    print("\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    with open(output_file, "rb") as video_file:
        file_contents = video_file.read()

        file_type = magic.from_buffer(buffer=file_contents, mime=True)

        file_extension = _constants.SUPPORT_FILE_TYPES[file_type]

        if isinstance(file_extension, list):
            file_extension = file_extension[
                0
            ]  # Lấy phần mở rộng đầu tiên trong danh sách
        print("\n file: ", file_extension)
        file_key = f"{uuid.uuid4()}.{file_extension}"

        video_url = await s3_upload(
            contents=file_contents, key=file_key, mime_type="video/mp4"
        )

    return video_url


def upload_video_to_s3(output_file: str):
    """
    Upload video lên S3 và trả về URL của video.
    """
    loop = asyncio.get_event_loop()  # Lấy loop hiện tại
    return loop.run_until_complete(upload_video_to_s3_async(output_file))


def convert_video_to_mp4(input_file):
    """
    Hàm chuyển đổi video đã ghi sang định dạng MP4 với codec h.264 và AAC
    """
    output_file = input_file.replace(".mp4", "_converted.mp4")

    # Câu lệnh FFmpeg để chuyển đổi video
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        input_file,  # Đầu vào
        "-c:v",
        "libx264",  # Sử dụng codec h.264
        "-c:a",
        "aac",  # Sử dụng codec AAC cho âm thanh
        "-strict",
        "experimental",  # Đảm bảo hỗ trợ AAC
        "-b:v",
        "1000k",  # Đặt bitrate video (có thể thay đổi tùy nhu cầu)
        "-b:a",
        "192k",  # Đặt bitrate âm thanh
        "-y",  # Ghi đè file đầu ra nếu đã tồn tại
        output_file,  # File đầu ra
    ]

    # Thực thi câu lệnh FFmpeg
    subprocess.run(ffmpeg_command, check=True)

    print(f"Video đã được chuyển đổi và lưu tại: {output_file}")
    
    return output_file
