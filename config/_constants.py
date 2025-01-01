from supervision import Point

# --------------------File Path------------------------#
VIDEO_PATH = "./file_path/video_stream"

MODEL_PATH = "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"  # "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"

AWS_BUCKET_NAME = "myawbucket1gg"


SUPPORT_FILE_TYPES = {
    "video/mp4": "mp4",
    "video/avi": "avi",
    "video/mkv": "mkv",
    "image/png": "png",
    "image/jpeg": ["jpg", "jpeg"],
}

CLOUDFRONT_BASE_URL = (
    "https://d5nvd4drtg1ie.cloudfront.net/"
)

# LINE_START = Point(670, 0)
# LINE_END = Point(670, 750)

# LINE_START = Point(350, 0)
# LINE_END = Point(350, 650)

LINE_START = Point(150, 0)
LINE_END = Point(150, 500)

WASTE_COUNT = {
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
