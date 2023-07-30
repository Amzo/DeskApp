import time

import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class PoseDetection(QThread):
    process_image_signal = pyqtSignal()
    image_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.how_many_frames = 2
        self.frame_count = 0
        self.image = None
        self.enabled = False
        self.results = None

        self.pose_mesh = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)

        self.process_image_signal.connect(self.process_image)
        self.image_signal.connect(self.update_image_and_process)

    def run(self):
        pass

    def process_image(self):
        self.results = self.pose_mesh.process(self.image[:, :, ::-1])

        self.frame_count = 0

    def update_image_and_process(self, eye_img):
        self.image = eye_img
        self.process_image_signal.emit()

    def stop(self):
        self.process_image_signal.disconnect(self.process_image)  # Disconnect the signal

    def get_default_image(self):
        return np.zeros((480, 640, 3), dtype=np.uint8)


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
