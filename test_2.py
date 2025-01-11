# from yolo_model.controllers._upload_video_s3 import convert_video_to_mp4 as convert_mp4
# from config import _create_file
# from yolo_model.controllers import _upload_video_s3


# file_path = "./file_path/video_stream/output_20241203_221002.mp4"

# # uploaf = convert_mp4(file_path)

# file = _create_file.return_file_name(file_path)
# # print(file)
# # out_put = _upload_video_s3.upload_video_to_s3_async(uploaf)
# # from supervision import Point
# # LINE_START = Point(670, 0)
# # print(LINE_START)
# # LINE_END = Point(670, 750)

# from yolo_model.controllers import _trigger_to_db
# from database.dependencies.dependencies import get_db
# from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
# from database.models.RacThai import RacThai
# from database.dependencies.dependencies import get_db
# from database.models.Camera import Camera
# from database.models.DanhMucMoHinh import DanhMucMoHinh
# from database.models.VideoXuLy import VideoXuLy
# from database.models.ChiTietXuLyRac import ChiTietXuLyRac
# from yolo_model.controllers import _save_to_db

# id = _trigger_to_db.get_id_waste_from_class_name("chai-nhua")
# print(id)
# with next(get_db()) as db:
#         result = (
#             db.query(RacThai.maRacThai)
#             .filter_by(maRacThaiQuyChieu="chai-nhua")
#             .first()
#         )
# print(result)
# file_name = "output_20241230_214454"
# cloudfront_url = (
#     "https://d5nvd4drtg1ie.cloudfront.net/93b3d5ef-b178-4038-93dd-19a7f36d5446.mp4"
# )
# start_time = "2024-12-30 21:44:41"

# end_time = "2024-12-30 21:47:41"

# video_duration = "180.872417"
# id = _save_to_db.save_video_process_db(file, cloudfront_url, start_time, end_time, video_duration)
# # _save_to_db.save_details_wastes_process_db('1', '1', 10, )
# print(id)

# idVideo = _save_to_db.save_video_process_db(
#     file_name,
#     cloudfront_url,
#     start_time,
#     end_time,
#     video_duration,
# )
# print("\nLưu video thành công, id_video: ", idVideo)

# from yolo_model.controllers import _upload_s3

# file = "./file_path/video_stream/output_20241204_211047_converted.mp4"

# up = _upload_s3.upload_img_to_s3(file)
# print("\n ", up)
# test = _upload_s3.convert_cloudfront_link(up)
# print(test)

# import requests

# url = "https://fae9-113-22-86-22.ngrok-free.app/1"
# headers = {"ngrok-skip-browser-warning": "true"}

# response = requests.get(url, headers=headers)
# print(response.text)
# print("aaaaaaaaaa")

from yolo_model.controllers._img_detect import detect_image, generate_stream_with_detection
from config import _create_file, _constants

img = "./file_path/img/Screenshot 2025-01-04 231456.png"
output = _constants.IMG_PATH

file, dete = detect_image(img, _constants.MODEL_PATH_3, output)
print("Link: ", file)
print("\nDetection: ", dete)

# video = "./output_frames/6779842421098717812.mp4"
# file= generate_stream_with_detection(video, _constants.MODEL_PATH_3)
# print("Link: ", file)

# from ultralytics import YOLO

# model_path = "./train_p3/train/weights/best.pt"
# try:
#     model = YOLO(model_path)
#     print("Mô hình đã được tải thành công!")
# except Exception as e:
#     print(f"Lỗi khi tải mô hình: {e}")