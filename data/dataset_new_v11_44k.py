from roboflow import Roboflow
rf = Roboflow(api_key="7iLd2NW8SnVygMHxf5sz")
project = rf.workspace("projectgraduation").project("phan-loai-rac-m7npu")
version = project.version(4)
dataset = version.download("yolov11")
                