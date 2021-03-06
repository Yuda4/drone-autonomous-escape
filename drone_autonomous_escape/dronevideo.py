import av
import numpy as np
import cv2
import time
import threading
from drone_autonomous_escape import GetObject
from drone_autonomous_escape import Config
import detect_model.brown_detection as detector


class DroneVideo(object):

    def __init__(self, drone):
        self.h = 700
        # image ratio is 960:720
        self.w = self.h + int(self.h / 3)
        self.drone = drone
        self.container = None
        self.retry = 3
        self.frame_skip = 300
        self.flag_show = False
        self.vid = None
        self.grid = True
        self.new_val = False
        # self.object = GetObject(config=Config())
        self.object_coords = None
        self.out = None
        self.export_flag = False
        self.frame_out = None
        self.setup()

    def set_export_vid(self, name):
        self.export_flag = True
        self.out = cv2.VideoWriter(name + ".avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 4, (self.w, self.h))

    def setup(self):

        while self.container is None and 0 < self.retry:

            self.retry -= 1
            try:
                self.container = av.open(self.drone.get_video_stream())
                threading.Thread(target=self.loop).start()
            except av.AVError as ave:
                print(ave)
                print('retry...')
        # cant get video
        return self.container is not None

    def loop(self):

        if self.container is not None:

            for frame in self.container.decode(video=0):

                if 0 < self.frame_skip:
                    self.frame_skip = self.frame_skip - 1
                    continue
                start_time = time.time()
                frm = np.array(frame.to_image())
                min_x, min_y = frm.shape[:2]
                mid_img = cv2.cvtColor(frm, cv2.COLOR_RGB2BGR)
                # use color detector.
                vid = detector.track_obj(frame=mid_img, min_x=min_x, min_y=min_y, max_x=0, max_y=0, drone=self.drone)
                self.vid = cv2.resize(vid, (self.w, self.h))

                # self.object.set_vid(self.vid)
                # self.object.update()
                # self.object_coords = self.object.get_coords()
                # self.new_val = self.object.is_new()
                self.flag_show = True
                if self.export_flag:
                    self.out.write(self.vid)
                if frame.time_base < 1.0 / 60:
                    time_base = 1.0 / 60
                else:
                    time_base = frame.time_base
                self.frame_skip = int((time.time() - start_time) / time_base)

    def show_vid(self):
        if self.flag_show:
            cv2.imshow("drone_vid", self.vid)
            cv2.waitKey(1)

    def get_coords(self):
        return self.object_coords

    def get_coords_pixel(self):
        return self.object.obj_pixel

    def is_new(self):
        return self.new_val
