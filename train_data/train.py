from ultralytics import YOLO

# Load a COCO-pretrained YOLOv8n model
model = YOLO("yolov8x.pt")

# Train the model on the COCO8 example dataset for 100 epochs
results = model.train(data="/home/ubuntu/yolo_train/waste_detect/data/phan-loai-rac-2/data.yaml", epochs=300, imgsz=640, lr0=0.0015, project="/home/ubuntu/yolo_train/waste_detect/train_data/checkpoints", name="waste_detection_v2")