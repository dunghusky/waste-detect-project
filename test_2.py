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

id = _trigger_to_db.get_id_waste_from_class_name("chai-nhua")
print(id)
# with next(get_db()) as db:
#         result = (
#             db.query(RacThai.maRacThai)
#             .filter_by(maRacThaiQuyChieu="chai-nhua")
#             .first()
#         )
# print(result)
