import mediapipe as mp
import numpy as np


class PoseDetection:
    def __init__(self):
        self.how_many_frames = 4
        self.frame_count = 0
        self.mp_drawing = mp.solutions.drawing_utils

    def return_pose_Image(self, image):
        self.frame_count += 1
        if self.frame_count >= self.how_many_frames:
            pose_mesh = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)

            results = pose_mesh.process(image[:, :, ::-1])
            img_h, img_w = image.shape[:2]

            if results.pose_landmarks is not None:
                self.mp_drawing.draw_landmarks(image=image, landmark_list=results.pose_landmarks,
                                          connections=mp.solutions.pose.POSE_CONNECTIONS,
                                          landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 255, 255),
                                                                                       thickness=3, circle_radius=3),
                                          connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(49, 125, 237),
                                                                                         thickness=2, circle_radius=2))

                self.frame_count = 0
                return image
            else:
                return image

