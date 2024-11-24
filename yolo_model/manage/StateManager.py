from threading import Event, Lock

class StateManager:
    def __init__(self):
        self.output_file = None
        self.video_writer = None
        self.terminate_flag = False
        self.lock = Lock()  # Khóa để bảo vệ truy cập
        self.completed_event = Event()

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
            if self.video_writer:
                self.video_writer.release()
            self.video_writer = None
            self.completed_event.clear()  # Đặt lại trạng thái event


state = StateManager()
