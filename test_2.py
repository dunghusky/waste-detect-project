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
from yolo_model.controllers import _save_to_db

# id = _trigger_to_db.get_id_waste_from_class_name("chai-nhua")
# print(id)
# with next(get_db()) as db:
#         result = (
#             db.query(RacThai.maRacThai)
#             .filter_by(maRacThaiQuyChieu="chai-nhua")
#             .first()
#         )
# print(result)
file = "output_20241230_114322"
cloudfront_url = (
    "https://d5nvd4drtg1ie.cloudfront.net/97fbbfb9-cad3-4ecb-b398-ee3184e135a0.mp4"
)
start_time = "2024-12-30 11:43:08.389374"

end_time = "2024-12-30 11:44:45.916455"

video_duration = "97.5270812"
id = _save_to_db.save_video_process_db(file, cloudfront_url, start_time, end_time, video_duration)
# _save_to_db.save_details_wastes_process_db('1', '1', 10, )
print(id)

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
