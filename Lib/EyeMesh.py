import itertools

import mediapipe as mp
import numpy as np
import cv2
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates


class EyeMesh:
    def __init__(self):
        self.how_many_frames = 4
        self.frame_count = 0

    def return_Iris_Image(self, image):
        self.frame_count += 1
        if self.frame_count >= self.how_many_frames:
            LEFT_IRIS = [474, 475, 476, 477]
            RIGHT_IRIS = [469, 470, 471, 472]

            face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1,
                                                        refine_landmarks=True,
                                                        min_detection_confidence=0.6,
                                                        min_tracking_confidence=0.6)

            results = face_mesh.process(image[:, :, ::-1])

            # getting width and height or frame
            img_h, img_w = image.shape[:2]

            if results.multi_face_landmarks is not None:
                mesh_points = np.array(
                    [np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in
                     results.multi_face_landmarks[0].landmark])

                (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
                (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])
                # turn center points into np array
                center_left = np.array([l_cx, l_cy], dtype=np.int32)
                center_right = np.array([r_cx, r_cy], dtype=np.int32)

                cv2.circle(image, center_left, int(l_radius), (0, 0, 255), 2, cv2.LINE_AA)
                cv2.circle(image, center_right, int(r_radius), (0, 0, 255), 2, cv2.LINE_AA)

                self.frame_count = 0
                return image
            else:
                self.frame_count = 0
                return image
