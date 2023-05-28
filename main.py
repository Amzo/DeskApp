import math
import sys

import cv2
import mediapipe as mp
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from GUI import Main
from GUI import VideoPlayer
from GUI.Camera import VideoThread
from Lib.Connection import ConnectPi
from Lib.EyeMesh import EyeMesh, EyePosition
from Lib.PoseDetection import PoseDetection, PosePosition


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Connect here
        self.connection = ConnectPi("10.42.0.1", 1883)
        #self.connection.connect_to_pi()

        self.ui = Main.Ui_MainWindow()
        self.ui.setupUi(self)

        self.mediaPlayer = VideoPlayer.VideoWindow(self.ui.VideoWidget)
        self.mediaPlayer.playback_slider_signal.connect(self.slider_update)
        self.mediaPlayer.playback_duration_signal.connect(self.video_duration)

        self.ui.playButton.clicked.connect(self.play)
        self.ui.pauseButton.clicked.connect(self.pause)

        # Camera stuff
        self.display_width = 640  # QDesktopWidget().screenGeometry().width()
        self.display_height = 360  # QDesktopWidget().screenGeometry().height()

        ### Tab widget ###
        self.ui.tabWidget.currentChanged.connect(self.onChange)
        ##################

        ### Video Thread ###
        # create the video capture thread
        self.videoThread = VideoThread()
        # connect its signal to the update_image slot
        self.videoThread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.videoThread.start()
        #####################

        ### Eye Tracking ###
        self.eyeTrackThread = EyeMesh()
        self.eyeTrackThread.toggle_pixmap_signal.connect(self.unblock_signal)
        self.eyeTrackThread.start()

        self.eyePos = EyePosition()
        self.eyeMesh = False
        self.start_point = (270, 160)
        self.end_point = (370, 200)

        # 50 - 60, 60 - 70, 70- 80
        self.ui.eye_track_button.clicked.connect(self.toggleEyeTrack)
        self.ui.eye_mesh_button.clicked.connect(self.toggleEyeMesh)
        ####################

        ### Pose Detection ###
        self.mp_drawing = mp.solutions.drawing_utils

        self.poseTrackThread = PoseDetection()
        self.poseTrackThread.toggle_pixmap_signal.connect(self.unblock_signal)
        self.poseTrackThread.start()

        self.posePos = PosePosition()
        self.poseMesh = False

        self.ui.pose_track_button.clicked.connect(self.togglePoseTrack)
        self.ui.pose_mesh_button.clicked.connect(self.togglePoseMesh)

    def toggleEyeTrack(self):
        self.connection.send_message("red")
        if self.ui.eye_track_button.isChecked():
            self.ui.eye_track_button.setStyleSheet("background-color : lightgreen")
        else:
            self.ui.eye_track_button.setStyleSheet("background-color : lightgrey")

        self.eyeTrackThread.enabled = not self.eyeTrackThread.enabled

    def toggleEyeMesh(self):
        if self.ui.eye_mesh_button.isChecked():
            self.ui.eye_mesh_button.setStyleSheet("background-color : lightgreen")
        else:
            self.ui.eye_mesh_button.setStyleSheet("background-color : lightgrey")

        self.eyeMesh = not self.eyeMesh

    def togglePoseTrack(self):
        self.connection.send_message("green")
        if self.ui.pose_track_button.isChecked():
            self.ui.pose_track_button.setStyleSheet("background-color : lightgreen")
        else:
            self.ui.pose_track_button.setStyleSheet("background-color : lightgrey")

        self.poseTrackThread.enabled = not self.poseTrackThread.enabled

    def togglePoseMesh(self):
        if self.ui.pose_mesh_button.isChecked():
            self.ui.pose_mesh_button.setStyleSheet("background-color : lightgreen")
        else:
            self.ui.pose_mesh_button.setStyleSheet("background-color : lightgrey")

        self.poseMesh = not self.poseMesh

    def play(self):
        self.ui.playButton.setStyleSheet("background-color : lightblue")
        self.ui.pauseButton.setStyleSheet("background-color : lightgrey")
        self.mediaPlayer.mediaPlayer.play()

    def pause(self):
        self.ui.pauseButton.setStyleSheet("background-color : lightblue")
        self.ui.playButton.setStyleSheet("background-color : lightgrey")
        self.mediaPlayer.mediaPlayer.pause()

    def slider_update(self, position):
        self.ui.VideoSlider.setSliderPosition(position)

        # ensure we have nice rounded numbers in mm:ss format for slider
        minutes, seconds = self.convert_seconds(round(position / 1000))
        t_minutes, t_seconds = self.convert_seconds(round(self.ui.VideoSlider.maximum() / 1000))

        if seconds < 10:
            timex = f"{minutes}0{seconds}"
            self.ui.durationLabel.setText(f'{minutes}:0{seconds} / {t_minutes}:{t_seconds}')
        else:
            self.ui.durationLabel.setText(f'{minutes}:{seconds} / {t_minutes}:{t_seconds}')
            timex = f"{minutes}{seconds}"

        #########################################################################################################
        # Send command to pi from here
        #########################################################################################################

        print(timex)
        if timex == "053":
            print("sending message")
            self.connection.send_message("pink")
        elif timex == "206":
            print("Sending message")
            self.connection.send_message("green")
        elif timex == "225":
            print("sending message")
            self.connection.send_message("blue")
        elif timex == "103" or timex == "220" or timex == "238":
            self.connection.send_message("off")

    @staticmethod
    def convert_seconds(seconds):
        hours = math.floor(seconds / 3600)
        minutes = math.floor((seconds - (hours * 3600)) / 60)
        secs = seconds - (hours * 3600) - (minutes * 60)

        return minutes, secs

    def video_duration(self, duration):
        self.ui.VideoSlider.setRange(0, duration)

    def onChange(self, i):  # changed!
        if i == 0:
            self.play()
            # self.tab_widget.camera.blockSignals(True)
            # self.tab_widget.camera.videoThread.pause = True
        if i == 1:
            self.pause()
            # self.tab_widget.camera.blockSignals(False)
            # self.tab_widget.camera.videoThread.pause = False
            # self.tab_widget.camera.thread.blockSignals(False)

    def drawRectangle(self, image):
        img = cv2.rectangle(image, self.start_point, self.end_point, (0,0, 255), 1)
        return img

    def setNewBoundingBox(self, distance):
        if 50 <= distance < 60:
            self.start_point = (250, 140)
            self.end_point = (390, 220)
        elif 60 <= distance < 70:
            self.start_point = (270, 160)
            self.end_point = (370, 200)
        elif 70 <= distance < 80:
            self.start_point = (290, 160)
            self.end_point = (350, 200)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        eye_img = None
        pose_img = None
        result = False

        if self.eyeTrackThread.enabled:
            self.eyeTrackThread.frame_count += 1
            eye_img = cv_img.copy()

            if self.eyeTrackThread.distance is not None:
                self.setNewBoundingBox(math.ceil(self.eyeTrackThread.distance))
                cv2.putText(eye_img,
                            f'{math.ceil(self.eyeTrackThread.distance)} cm',
                            (10,20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA)

            img_w, img_h = eye_img.shape[:2]
            if self.eyeTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.eyeTrackThread.image = eye_img

            # load cached eyes
            if self.eyeTrackThread.left_eye[0] > 0 and self.eyeTrackThread.right_eye[0] > 0:

                if self.eyeTrackThread.left_eye[0] > self.start_point[0] and self.eyeTrackThread.left_eye[1] > self.start_point[1]:
                    left_eye = True
                else:
                    left_eye = False

                if self.eyeTrackThread.right_eye[0] <= self.end_point[0] and self.eyeTrackThread.right_eye[1] < self.end_point[1]:
                    right_eye = True
                else:
                    right_eye = False

                if right_eye and left_eye:
                    result = True
                else:
                    result = False

                if self.eyeMesh:
                    eye_img = self.drawRectangle(eye_img)

                    cv2.circle(eye_img, self.eyeTrackThread.left_eye, int(self.eyeTrackThread.l_radius), (0, 255, 0), 2,
                               cv2.LINE_AA)
                    cv2.circle(eye_img, self.eyeTrackThread.right_eye, int(self.eyeTrackThread.r_radius), (0, 255, 0),
                               2,
                               cv2.LINE_AA)

            if result:
                cv2.line(eye_img, (630, 310), (610, 340), (52, 255, 52), 2)
                cv2.line(eye_img, (610, 340), (600, 325), (52, 255, 52), 2)
                # cv2.line(eye_img, (600, 400), (585, 430), (52,255,52), 2)
                # cv2.line(eye_img, (585, 430), (580, 420), (52,255,52), 2)
            else:
                cv2.line(eye_img, (630, 310), (610, 340), (0, 0, 255), 2)
                cv2.line(eye_img, (610, 310), (630, 340), (0, 0, 255), 2)
                # cv2.imshow("derp", image)

                # cv2.line(eye_img, (width, 0), (0, height), (0, 0, 255), 5)

        # if pose detection is enabled
        if self.poseTrackThread.enabled:
            self.poseTrackThread.frame_count += 1
            pose_img = cv_img.copy()

            if self.poseTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.poseTrackThread.image = pose_img

            if self.poseTrackThread.results is not None:
                results = self.posePos.calculate(self.poseTrackThread.results.pose_landmarks)
                if self.poseMesh:
                    self.mp_drawing.draw_landmarks(image=pose_img,
                                                   landmark_list=self.poseTrackThread.results.pose_landmarks,
                                                   connections=mp.solutions.pose.POSE_CONNECTIONS,
                                                   landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(255, 255, 255),
                                                       thickness=3, circle_radius=3),
                                                   connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(49, 125, 237),
                                                       thickness=2, circle_radius=2))

                if results:
                    cv2.line(pose_img, (630, 310), (610, 340), (52, 255, 52), 2)
                    cv2.line(pose_img, (610, 340), (600, 325), (52, 255, 52), 2)
                    # cv2.line(eye_img, (600, 400), (585, 430), (52,255,52), 2)
                    # cv2.line(eye_img, (585, 430), (580, 420), (52,255,52), 2)
                else:
                    cv2.line(pose_img, (630, 310), (610, 340), (0, 0, 255), 2)
                    cv2.line(pose_img, (610, 310), (630, 340), (0, 0, 255), 2)

        if eye_img is not None:
            eye_img = self.convert_cv_qt(eye_img)
            self.ui.lblCameraEye.setPixmap(eye_img)
            eye_img = None
        else:
            qt_img = self.convert_cv_qt(cv_img)
            self.ui.lblCameraEye.setPixmap(qt_img)

        if pose_img is not None:
            pose_img = self.convert_cv_qt(pose_img)
            self.ui.lblCameraPose.setPixmap(pose_img)
        else:
            qt_img = self.convert_cv_qt(cv_img)
            self.ui.lblCameraPose.setPixmap(qt_img)

    @pyqtSlot(int)
    def unblock_signal(self):
        self.videoThread.blockSignals(False)

    @pyqtSlot(int)
    def add_tick(self):
        self.tick = True

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.IgnoreAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MainWindow()
    player.showMaximized()
    sys.exit(app.exec_())
