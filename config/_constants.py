from supervision import Point

# --------------------File Path------------------------#
VIDEO_PATH = "./file_path/video_stream"

IMG_PATH = "./file_path/img"

MODEL_PATH = "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt" #"./train/weights/best.pt" #"./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"  # "./yolo_model/checkpoints/waste_detection_v2/weights/best.pt"

MODEL_PATH_2 = "./train_p2/train/weights/best.pt"
MODEL_PATH_3 = "./train_p3/train/weights/best.pt"

AWS_BUCKET_NAME = "myawbucket1gg"


SUPPORT_FILE_TYPES = {
    "video/mp4": "mp4",
    "video/avi": "avi",
    "video/mkv": "mkv",
    "image/png": "png",
    "image/jpeg": ["jpg", "jpeg"],
    "text/csv": "csv",
    "text/plain": "csv"
}

CLOUDFRONT_BASE_URL = (
    "https://d5nvd4drtg1ie.cloudfront.net/"
)

# LINE_START = Point(670, 0)
# LINE_END = Point(670, 750)

# LINE_START = Point(350, 0)
# LINE_END = Point(350, 650)

LINE_START = Point(200, 0)
LINE_END = Point(200, 500)

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
