from yolo_model.controllers._upload_video_s3 import convert_video_to_mp4 as convert_mp4
from config import _create_file
from yolo_model.controllers import _upload_video_s3


file_path = "./file_path/video_stream/output_20241203_221002.mp4"

# uploaf = convert_mp4(file_path)

file = _create_file.return_file_name(file_path)
print(file)
# out_put = _upload_video_s3.upload_video_to_s3_async(uploaf)
