import math
import sys
import time

import cv2
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

from GUI import Main
from GUI import VideoPlayer
from GUI.Camera import VideoThread

import mediapipe as mp

from Lib.EyeMesh import EyeMesh, EyePosition
from Lib.PoseDetection import PoseDetection




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Main.Ui_MainWindow()
        self.ui.setupUi(self)

        self.mediaPlayer = VideoPlayer.VideoWindow(self.ui.VideoWidget)
        self.mediaPlayer.playback_slider_signal.connect(self.slider_update)
        self.mediaPlayer.playback_duration_signal.connect(self.video_duration)

        self.ui.playButton.clicked.connect(self.play)
        self.ui.pauseButton.clicked.connect(self.pause)

        # Camera stuff
        self.display_width = 640  # QDesktopWidget().screenGeometry().width()
        self.display_height = 480  # QDesktopWidget().screenGeometry().height()

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

        self.ui.eye_track_button.clicked.connect(self.toggleEyeTrack)
        self.ui.eye_mesh_button.clicked.connect(self.toggleEyeMesh)
        ####################

        ### Pose Detection ###
        self.mp_drawing = mp.solutions.drawing_utils

        self.poseTrackThread = PoseDetection()
        self.poseTrackThread.toggle_pixmap_signal.connect(self.unblock_signal)
        self.poseTrackThread.start()
        self.poseMesh = False

        self.ui.pose_track_button.clicked.connect(self.togglePoseTrack)
        self.ui.pose_mesh_button.clicked.connect(self.togglePoseMesh)

    def toggleEyeTrack(self):
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
            self.ui.durationLabel.setText(f'{minutes}:0{seconds} / {t_minutes}:{t_seconds}')
        else:
            self.ui.durationLabel.setText(f'{minutes}:{seconds} / {t_minutes}:{t_seconds}')

        #########################################################################################################
        # Send command to pi from here
        #########################################################################################################

    @staticmethod
    def convert_seconds(seconds):
        hours = math.floor(seconds / 3600)
        minutes = math.floor((seconds - (hours * 3600)) / 60)
        secs = seconds - (hours * 3600) - (minutes * 60)

        return minutes, seconds

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

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        eye_img = None
        pose_img = None

        if self.eyeTrackThread.enabled:
            self.eyeTrackThread.frame_count += 1
            eye_img = cv_img.copy()
            if self.eyeTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.eyeTrackThread.image = eye_img

            # load cached eyes
            if self.eyeTrackThread.left_eye[0] > 0 and self.eyeTrackThread.right_eye[0] > 0:
                result = self.eyePos.center_calculations(
                    self.eyeTrackThread.left_eye[0] + self.eyeTrackThread.right_eye[0],
                    self.eyeTrackThread.left_eye[1] + self.eyeTrackThread.right_eye[1])

                if self.eyeMesh:
                    cv2.circle(eye_img, self.eyeTrackThread.left_eye, int(self.eyeTrackThread.l_radius), (0, 0, 255), 2,
                               cv2.LINE_AA)
                    cv2.circle(eye_img, self.eyeTrackThread.right_eye, int(self.eyeTrackThread.r_radius), (0, 0, 255),
                               2,
                               cv2.LINE_AA)

        #        print(result)
        #        # if self.tick:
        #        #    print("ok")
        #        cv2.putText(img=cv_img, text='OK', org=(480 - 30, 640 - 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        #                    fontScale=3,
        #                    color=(52, 235, 52), thickness=3)

        # if pose detection is enabled
        if self.poseTrackThread.enabled:
            self.poseTrackThread.frame_count += 1
            pose_img = cv_img.copy()

            if self.poseTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.poseTrackThread.image = pose_img

            if self.poseTrackThread.results is not None:
                if self.poseMesh:
                    print("drawing pose")
                    self.mp_drawing.draw_landmarks(image=pose_img,
                                                   landmark_list=self.poseTrackThread.results.pose_landmarks,
                                                   connections=mp.solutions.pose.POSE_CONNECTIONS,
                                                   landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(255, 255, 255),
                                                       thickness=3, circle_radius=3),
                                                   connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(49, 125, 237),
                                                       thickness=2, circle_radius=2))

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

    # def resizeEvent(self, event):
    #    self.display_width = self.ui.lblCameraEye.width()
    #    self.display_height = self.ui.lblCameraEye.height()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MainWindow()
    player.showMaximized()
    sys.exit(app.exec_())
