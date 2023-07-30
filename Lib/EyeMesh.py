import math
import time

import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, QTimer, pyqtSignal


class EyeMesh(QThread):
    process_image_signal = pyqtSignal()
    image_signal = pyqtSignal(np.ndarray)
    eyes_detected_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.last_detection_time = None
        self.result = None
        self.distance = None
        self.how_many_frames = 2
        self.frame_count = 0
        self.left_eye = np.array([0, 0])
        self.right_eye = np.array([0, 0])
        self.center_position = np.array([0, 0])
        self.l_radius = 0
        self.r_radius = 0
        self.image = self.get_default_image()

        self.KNOWN_DISTANCE = 64  # cm
        self.KNOWN_WIDTH = 6.4  # cm
        self.BASE_EYE_DISTANCE_PIXELS = 52  # cm
        self.focal_length = (self.BASE_EYE_DISTANCE_PIXELS * self.KNOWN_DISTANCE) / self.KNOWN_WIDTH

        self.process_image_signal.connect(self.process_image)
        self.image_signal.connect(self.update_image_and_process)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_last_detection_time)
        self.timer.start(1000)  # Check every 1 second (1000 milliseconds)

        # default bounding box
        self.start_point = (270, 160)
        self.end_point = (370, 200)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True,
                                                         max_num_faces=1,
                                                         refine_landmarks=True,
                                                         min_detection_confidence=0.6,
                                                         min_tracking_confidence=0.6)

    def run(self):
        pass

    def check_last_detection_time(self):
        if self.last_detection_time is not None and time.time() - self.last_detection_time > 5:
            self.last_detection_time = None
            print("No one detected in 5 seconds")
            self.eyes_detected_signal.emit(False)

    def process_image(self):
        RIGHT_IRIS = [474, 475, 476, 477]
        LEFT_IRIS = [469, 470, 471, 472]

        self.center_position = np.array([self.image.shape[1] / 2, self.image.shape[0] / 2])

        results = self.face_mesh.process(self.image[:, :, ::-1])

        if results.multi_face_landmarks is not None:
            mesh_points = np.array(
                [np.multiply([p.x, p.y], [self.image.shape[1], self.image.shape[0]]).astype(int) for p in
                 results.multi_face_landmarks[0].landmark])

            (l_cx, l_cy), self.l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), self.r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])

            eye_width_pixels = r_cx - l_cx
            self.distance = (self.KNOWN_WIDTH * self.focal_length) / eye_width_pixels

            self.left_eye = np.array([l_cx, l_cy], dtype=np.int32)
            self.right_eye = np.array([r_cx, r_cy], dtype=np.int32)

            self.last_detection_time = time.time()
            self.eyes_detected_signal.emit(True)
        else:
            self.eyes_detected_signal.emit(False)

        self.frame_count = 0

    def update_image_and_process(self, eye_img):
        self.image = eye_img.copy()
        self.process_image_signal.emit()

    def stop(self):
        self.process_image_signal.disconnect(self.process_image)  # Disconnect the signal

    def get_default_image(self):
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def perform_calculations(self):
        # load cached eyes
        if self.left_eye[0] > 0 and self.right_eye[0] > 0:

            if self.left_eye[0] > self.start_point[0] and self.left_eye[1] > \
                    self.start_point[1]:
                left_eye = True
            else:
                left_eye = False

            if self.right_eye[0] <= self.end_point[0] and self.right_eye[1] < \
                    self.end_point[1]:
                right_eye = True
            else:
                right_eye = False

            if right_eye and left_eye:
                self.result = True
            else:
                self.result = False

            eye_img = self.drawRectangle()

            cv2.circle(eye_img, self.left_eye, int(self.l_radius), (0, 255, 0), 2,
                       cv2.LINE_AA)
            cv2.circle(eye_img, self.right_eye, int(self.r_radius), (0, 255, 0),
                       2,
                       cv2.LINE_AA)

            self.setNewBoundingBox(math.ceil(self.distance), self.image.shape[1], self.image.shape[0])
            self.left_eye = (0, 0)
            self.right_eye = (0, 0)

    def drawRectangle(self):
        img = cv2.rectangle(self.image, self.start_point, self.end_point, (0, 0, 255), 1)
        return img

    def setNewBoundingBox(self, distance, image_width, image_height):
        # Check if distance is within the specified range
        if 50 <= distance < 80:
            min_start_point = (310 * 1.2, 180 * 1.2)  # increased by 10%
            max_start_point = (250, 140)
            min_end_point = (370 * 1.2, 220 * 1.2)  # increased by 10%
            max_end_point = (450, 220)

            # Calculate ratio based on distance
            ratio = 1 - (distance - 50) / (80 - 50)  # inverse ratio

            # Calculate new start and end points using linear interpolation
            min_width = min_end_point[0] - min_start_point[0]
            max_width = max_end_point[0] - max_start_point[0]
            min_height = min_end_point[1] - min_start_point[1]
            max_height = max_end_point[1] - max_start_point[1]

            box_width = int(min_width + ratio * (max_width - min_width))
            box_height = int(min_height + ratio * (max_height - min_height))

            # Calculate new start and end points based on image center
            half_width = image_width // 2
            half_height = image_height // 2

            self.start_point = (half_width - box_width // 2, half_height - box_height // 2)
            self.end_point = (half_width + box_width // 2, half_height + box_height // 2)


class EyePosition:
    def __init__(self):
        self.center_threshold = 50
        self.center_position = [320, 240]

    def center_calculations(self, eye_left_right, eye_up_down):
        if self.center_position[0] - self.center_threshold <= \
                eye_left_right <= self.center_position[0] + self.center_threshold:
            eye_horizontal_aligned = True
        else:
            eye_horizontal_aligned = False

        if self.center_position[1] - self.center_threshold <= \
                eye_up_down <= self.center_position[1] + self.center_threshold:
            eye_vertical_aligned = True
        else:
            eye_vertical_aligned = False

        if eye_vertical_aligned and eye_horizontal_aligned is True:
            return True
        else:
            return False
