# from yolo_model.controllers._upload_video_s3 import convert_video_to_mp4 as convert_mp4
# from config import _create_file
# from yolo_model.controllers import _upload_video_s3


# file_path = "./file_path/video_stream/output_20241203_221002.mp4"

# # uploaf = convert_mp4(file_path)

# file = _create_file.return_file_name(file_path)
# print(file)
# out_put = _upload_video_s3.upload_video_to_s3_async(uploaf)
# from supervision import Point
# LINE_START = Point(670, 0)
# print(LINE_START)
# LINE_END = Point(670, 750)

from yolo_model.controllers import _trigger_to_db
from database.dependencies.dependencies import get_db
from database.models.DanhMucPhanLoaiRac import DanhMucPhanLoaiRac
from database.models.RacThai import RacThai
from database.dependencies.dependencies import get_db
from database.models.Camera import Camera
from database.models.DanhMucMoHinh import DanhMucMoHinh
from database.models.VideoXuLy import VideoXuLy
from database.models.ChiTietXuLyRac import ChiTietXuLyRac
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
file = "output_20241217_221822"
cloudfront_url=  "https://d3cnmk90vb0eje.cloudfront.net/421aada1-d634-4ad9-98d2-0b6b7510278d.mp4"
start_time="2024-12-17 22:18:08.330587"

end_time= "2024-12-17 22:18:46.458299"

video_duration="38.127712"
id = _save_to_db.save_video_process_db(file, cloudfront_url, start_time, end_time, video_duration)
print(id)
