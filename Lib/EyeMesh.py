import itertools
import time

import mediapipe as mp
import numpy as np
import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates


class EyeMesh(QThread):
    toggle_pixmap_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.distance = None
        self.how_many_frames = 2
        self.frame_count = 0
        self.left_eye = [0, 0]
        self.right_eye = [0, 0]
        self.center_position = [0, 0]
        self.l_radius = 0
        self.r_radius = 0
        self.image = None
        self.enabled = False

        self.KNOWN_DISTANCE = 58.42 #cm
        self.KNOWN_WIDTH = 6.4 # cm

        # self.Positionthread = EyePosition(self)
        # self.Positionthread.start()

    def get_eye_width_in_pixels(self, left_eye, right_eye):
        return (right_eye - left_eye)

    def get_focal_length(self):
        return (54.5 * self.KNOWN_DISTANCE) / self.KNOWN_WIDTH

    def distance_finder(self, eye_distance):
        # off by approximately 2cm, so minus 2
        self.distance =  ((self.KNOWN_WIDTH * self.get_focal_length()) / eye_distance) - 2

    def run(self):
        RIGHT_IRIS = [474, 475, 476, 477]
        LEFT_IRIS = [469, 470, 471, 472]

        face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True,
                                                    max_num_faces=1,
                                                    refine_landmarks=True,
                                                    min_detection_confidence=0.6,
                                                    min_tracking_confidence=0.6)
        while True:
            time.sleep(0.1)
            if self.frame_count >= self.how_many_frames and self.image is not None:
                results = face_mesh.process(self.image[:, :, ::-1])

                # getting width and height or frame
                img_h, img_w = self.image.shape[:2]

                # center position based on webcam resolution, width and height divided by two
                self.center_position = [img_w / 2, img_h / 2]

                if results.multi_face_landmarks is not None:
                    mesh_points = np.array(
                        [np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in
                         results.multi_face_landmarks[0].landmark])

                    (l_cx, l_cy), self.l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
                    (r_cx, r_cy), self.r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])

                    # turn center points into np array
                    eye_width_pixels = self.get_eye_width_in_pixels(l_cx, r_cx)
                    self.distance_finder(eye_width_pixels)

                    self.left_eye = np.array([l_cx, l_cy], dtype=np.int32)
                    self.right_eye = np.array([r_cx, r_cy], dtype=np.int32)

                    # cv2.circle(self.image, self.left_eye, int(self.l_radius), (0, 0, 255), 2, cv2.LINE_AA)
                    # cv2.circle(self.image, self.right_eye, int(self.r_radius), (0, 0, 255), 2, cv2.LINE_AA)

                    # if self.Positionthread:
                    #    print("Drawing Tick")
                    #    cv2.putText(image, 'OK', (img_h - 30, img_w - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (52, 235, 52), 1, 2)
                    self.frame_count = 0
                    self.toggle_pixmap_signal.emit(1)
                    self.image = None
                else:
                    self.image = None
                    self.frame_count = 0
                    self.toggle_pixmap_signal.emit(1)


class EyePosition():
    def __init__(self):
        eye_distance = 64
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
