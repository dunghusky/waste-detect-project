class StateManager:
    def __init__(self):
        self.output_file = None
        self.video_writer = None
        self.terminate_flag = False

    def reset(self):
        self.terminate_flag = False
        self.output_file = None
        self.video_writer = None


state = StateManager()
