import cv2
import time
from threading import Thread


# class WebcamStream:
#     def __init__(self, stream_id=0):
#         self.stream_id = stream_id  # default is 0 for primary camera

#         # opening video capture stream
#         self.vcap = cv2.VideoCapture(self.stream_id)
#         if self.vcap.isOpened() is False:
#             print("[Exiting]: Error accessing webcam stream.")
#             exit(0)
#         fps_input_stream = int(self.vcap.get(5))
#         print("FPS of webcam hardware/input stream: {}".format(fps_input_stream))

#         # reading a single frame from vcap stream for initializing
#         self.grabbed, self.frame = self.vcap.read()
#         if self.grabbed is False:
#             print("[Exiting] No more frames to read")
#             exit(0)

#         # self.stopped is set to False when frames are being read from self.vcap stream
#         self.stopped = True

#         # reference to the thread for reading next available frame from input stream
#         self.t = Thread(target=self.update, args=())
#         self.t.daemon = True  # daemon threads keep running in the background while the program is executing

#     # method for starting the thread for grabbing next available frame in input stream
#     def start(self):
#         self.stopped = False
#         self.t.start()

#     # method for reading next frame
#     def update(self):
#         while True:
#             if self.stopped is True:
#                 break
#             self.grabbed, self.frame = self.vcap.read()
#             if self.grabbed is False:
#                 print("[Exiting] No more frames to read")
#                 self.stopped = True
#                 break
#         self.vcap.release()

#     # method for returning latest read frame
#     def read(self):
#         return self.frame

#     # method called to stop reading frames
#     def stop(self):
#         self.stopped = True


class WebcamStream:
    def __init__(self, stream_id=0, target_fps=30):
        self.stream_id = stream_id
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps  # Khoảng thời gian giữa 2 khung hình
        self.last_read_time = time.time()

        # opening video capture stream
        self.vcap = cv2.VideoCapture(self.stream_id)
        if self.vcap.isOpened() is False:
            print("[Exiting]: Error accessing webcam stream.")
            exit(0)
        fps_input_stream = int(self.vcap.get(5))
        print("FPS of webcam hardware/input stream: {}".format(fps_input_stream))

        # reading a single frame from vcap stream for initializing
        self.grabbed, self.frame = self.vcap.read()
        if self.grabbed is False:
            print("[Exiting] No more frames to read")
            exit(0)

        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def update(self):
        while True:
            if self.stopped is True:
                break
            current_time = time.time()
            if current_time - self.last_read_time >= self.frame_interval:
                self.grabbed, self.frame = self.vcap.read()
                self.last_read_time = current_time
            if self.grabbed is False:
                print("[Exiting] No more frames to read")
                self.stopped = True
                break
        self.vcap.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
