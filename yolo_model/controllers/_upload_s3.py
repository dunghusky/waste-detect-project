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


def s3_upload(contents: bytes, key: str, mime_type: str):
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


def upload_file_to_s3(output_file: str):
    """
    Upload video lên S3 và trả về URL của video.
    """
    with open(output_file, "rb") as video_file:
        file_contents = video_file.read()

        file_type = magic.from_buffer(buffer=file_contents, mime=True)

        file_extension = _constants.SUPPORT_FILE_TYPES[file_type]

        if isinstance(file_extension, list):
            file_extension = file_extension[
                0
            ]  # Lấy phần mở rộng đầu tiên trong danh sách
        file_key = f"{uuid.uuid4()}.{file_extension}"

        file_url = s3_upload(contents=file_contents, key=file_key, mime_type=file_type)

    return file_url


# Thay đổi URL từ S3 URL sang CloudFront URL
def convert_cloudfront_link(video_url):
    cloudfront_base_url = _constants.CLOUDFRONT_BASE_URL
    video_file_key = video_url.split("/")[-1]  # Lấy tên file từ S3 URL
    cloudfront_url = f"{cloudfront_base_url}{video_file_key}"
    return cloudfront_url


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
