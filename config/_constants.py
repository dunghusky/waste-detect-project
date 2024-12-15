from supervision import Point

# --------------------File Path------------------------#
VIDEO_PATH = "./file_path/video_stream"

AWS_BUCKET_NAME = "barberbuddy"


SUPPORT_FILE_TYPES = {
    "video/mp4": "mp4",
    "video/avi": "avi",
    "video/mkv": "mkv",
}

CLOUDFRONT_BASE_URL = "https://d3cnmk90vb0eje.cloudfront.net/"

LINE_START = Point(670, 0)
LINE_END = Point(670, 750)

waste_count = {
    "chai-lo-manh-vo-thuy-tinh": 0,
    "chai-nhua": 0,
    "hop-sua": 0,
    "khau-trang": 0,
    "lon-nuoc-giai-khat-bang-kim-loai": 0,
    "ly-nhua": 0,
    "rac-huu-co": 0,
    "tui-nilon": 0,
}

COUNTED_IDS= set()
