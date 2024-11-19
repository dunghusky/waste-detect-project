from ultralytics import YOLO

# Load a COCO-pretrained YOLOv8n model
model = YOLO("yolov8x.pt")

# Train the model on the COCO8 example dataset for 100 epochs
results = model.train(data="/home/ubuntu/yolo_train/waste-detect-project/data/phan-loai-rac-2/data.yaml", epochs=500, imgsz=640, lr0=0.0015, project="/home/ubuntu/yolo_train/waste-detect-project/train_data/checkpoints", name="waste_detection_v2")