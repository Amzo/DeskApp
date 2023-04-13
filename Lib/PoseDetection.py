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


class PosePosition():
    def __init__(self):
        self.center_threshold = 75

    def calculate(self, landmarks):

        if landmarks is not None:
            mesh_points = np.array(
                [np.multiply([p.x, p.y], [320, 240]).astype(int) for p in landmarks.landmark])
        else:
            return False

        mouth = (mesh_points[10] + mesh_points[9]) / 2
        shoulders = (mesh_points[12] + mesh_points[11]) / 2

        distance = shoulders[1] - mouth[1]

        if distance >= 40:
            return True
        else:
            return False

