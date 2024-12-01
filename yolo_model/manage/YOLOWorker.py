from threading import Thread
import time
from yolo_model.controllers import _stream_detect

class YOLOWorker(Thread):
    def __init__(self, model, input_queue, output_queue):
        super().__init__()
        self.model = model
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stopped = False

    def run(self):
        while not self.stopped:
            if not self.input_queue.empty():
                frame = self.input_queue.get()
                start_time = time.time()

                # Thực hiện inference YOLO
                detections = _stream_detect.detect_objects(frame, self.model)
                end_time = time.time()

                # Tính thời gian inference và đưa kết quả vào output_queue
                inference_time = end_time - start_time
                self.output_queue.put((detections, frame, inference_time))

    def stop(self):
        self.stopped = True
