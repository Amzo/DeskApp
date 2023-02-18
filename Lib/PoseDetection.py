import time

import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class PoseDetection(QThread):
    toggle_pixmap_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.how_many_frames = 2
        self.frame_count = 0
        self.image = None
        self.enabled = False
        self.results = None

        self.pose_mesh = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)

    def run(self):
        while True:
            time.sleep(0.04)
            if self.frame_count >= self.how_many_frames and self.image is not None:

                self.results = self.pose_mesh.process(self.image[:, :, ::-1])

                self.frame_count = 0
                self.toggle_pixmap_signal.emit(1)
            else:
                self.toggle_pixmap_signal.emit(1)


