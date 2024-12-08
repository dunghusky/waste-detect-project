from datetime import datetime
from threading import Event, Lock

class StateManager:
    def __init__(self):
        self.output_file = None
        self.video_writer = None
        self.terminate_flag = False
        self.lock = Lock()  # Khóa để bảo vệ truy cập
        self.completed_event = Event()

        self.start_time = None
        self.end_time = None

    # def set_start_time(self):
    #     """Gán thời gian bắt đầu quay video"""
    #     with self.lock:
    #         self.start_time = datetime.now()

    # def set_end_time(self):
    #     """Gán thời gian kết thúc quay video"""
    #     with self.lock:
    #         self.end_time = datetime.now()

    def set_video_writer(self, writer):
        with self.lock:
            self.video_writer = writer

    def get_video_writer(self):
        with self.lock:
            return self.video_writer

    def reset(self):
        with self.lock:
            self.terminate_flag = False
            self.output_file = None
            self.start_time = None
            self.end_time = None
            if self.video_writer:
                self.video_writer.release()
            self.video_writer = None
            self.completed_event.clear()  # Đặt lại trạng thái event


state = StateManager()
