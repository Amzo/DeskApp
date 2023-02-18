import os

import numpy as np
import cv2
from PyQt5 import QtGui
from PyQt5.QtCore import QDir, Qt, QUrl, QStandardPaths, QDate, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QGuiApplication, QDesktopServices, QImage, QIcon
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QMainWindow, QAction, QToolBar, \
    QComboBox, QDesktopWidget

import mediapipe as mp
from Lib import EyeMesh, PoseDetection


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.pause = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        while self._run_flag:
            if not self.pause:
                ret, cv_img = cap.read()
                cv_img = cv2.flip(cv_img, 1)
                if ret:
                    """I don't know how powerful the hardware will be, so limiting eye mesh tracking"""
                    self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class CameraWindow(QMainWindow):
    got_image_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(CameraWindow, self).__init__(parent)
        self.tick = None
        self.eyeMesh = False
        self.mp_drawing = mp.solutions.drawing_utils
        self.display_width = QDesktopWidget().screenGeometry().width()
        self.display_height = QDesktopWidget().screenGeometry().height()

        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)
        self.image_label.setGeometry(0, 0, self.display_width, self.display_height)
        # create a vertical box layout and add the two labels
        vbox = QHBoxLayout()
        vbox.addWidget(self.image_label)
        # set the vbox layout as the widgets layout

        self.EyeTrackButton = QPushButton("Enable Eye Tracking", self)
        self.EyeTrackButton.setGeometry(self.display_width, 0, 150, 40)
        self.EyeTrackButton.setCheckable(True)
        self.EyeTrackButton.clicked.connect(self.toggleEyeTrack)
        vbox.addWidget(self.EyeTrackButton)

        self.ToggleEyeMeshButton = QPushButton("Enable Eye Mesh", self)
        self.ToggleEyeMeshButton.setGeometry(self.display_width, 50, 150, 40)
        self.ToggleEyeMeshButton.setCheckable(True)
        self.ToggleEyeMeshButton.clicked.connect(self.toggleEyeMesh)
        vbox.addWidget(self.ToggleEyeMeshButton)

        self.PoseButton = QPushButton("Enable Pose Detection", self)
        self.PoseButton.setGeometry(self.display_width, 100, 150, 40)
        self.PoseButton.setCheckable(True)
        self.PoseButton.clicked.connect(self.togglePose)
        vbox.addWidget(self.PoseButton)

        self.combobox = QComboBox(self)

        for i in range(0, 24):
            self.combobox.addItem(str(i))

        self.combobox.currentTextChanged.connect(self.update_mesh_intervals)
        self.combobox.setCurrentIndex(4)
        self.combobox.setGeometry(self.display_width, 150, 150, 40)
        vbox.addWidget(self.combobox)

        # create the video capture thread
        self.videoThread = VideoThread()
        # connect its signal to the update_image slot
        self.videoThread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.videoThread.start()

        self.eyeTrackThread = EyeMesh.EyeMesh()
        self.eyeTrackThread.toggle_pixmap_signal.connect(self.unblock_signal)
        self.eyeTrackThread.start()


        self.poseTrackThread = PoseDetection.PoseDetection()
        self.poseTrackThread.toggle_pixmap_signal.connect(self.unblock_signal)
        self.poseTrackThread.start()
        self.eyePos = EyeMesh.EyePosition()
        #self.eyePos.correct_position.connect(self.add_tick)
        #self.eyePos.start()
        
        self.setLayout(vbox)

    def update_mesh_intervals(self, value):
        try:
            self.thread.eyeMesh.how_many_frames = int(value)
            self.thread.pose.how_many_frames = int(value)
        except AttributeError:
            pass

    def resizeEvent(self, event):
        self.EyeTrackButton.move(self.width() - self.EyeTrackButton.width() - 2, 0)
        self.PoseButton.move(self.width() - self.EyeTrackButton.width() - 2, 100)
        self.ToggleEyeMeshButton.move(self.width() - self.EyeTrackButton.width() - 2, 50)
        self.combobox.move(self.width() - self.EyeTrackButton.width() - 2, 150)
        self.display_width = self.width() - self.EyeTrackButton.width() - 17
        # self.display_height = self.height()
        # self.image_label.move(0,0)
        super(CameraWindow, self).resizeEvent(event)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def toggleEyeTrack(self):
        if self.EyeTrackButton.isChecked():
            self.EyeTrackButton.setStyleSheet("background-color : lightgreen")
        else:
            self.EyeTrackButton.setStyleSheet("background-color : lightgrey")

        self.eyeTrackThread.enabled = not self.eyeTrackThread.enabled

    def toggleEyeMesh(self):
        if self.ToggleEyeMeshButton.isChecked():
            self.ToggleEyeMeshButton.setStyleSheet("background-color : lightgreen")
        else:
            self.ToggleEyeMeshButton.setStyleSheet("background-color : lightgrey")

        self.eyeMesh = not self.eyeMesh
    def togglePose(self):
        if self.PoseButton.isChecked():
            self.PoseButton.setStyleSheet("background-color : lightblue")
        else:
            self.PoseButton.setStyleSheet("background-color : lightgrey")

        self.poseTrackThread.enabled = not self.poseTrackThread.enabled


    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""

        if self.eyeTrackThread.enabled:
            self.eyeTrackThread.frame_count += 1

            if self.eyeTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.eyeTrackThread.image = cv_img

            # load cached eyes
            if self.eyeTrackThread.left_eye[0] > 0 and self.eyeTrackThread.right_eye[0] > 0:
                result = self.eyePos.center_calculations(self.eyeTrackThread.left_eye[0] + self.eyeTrackThread.right_eye[0],
                                                self.eyeTrackThread.left_eye[1] + self.eyeTrackThread.right_eye[1])

                if self.eyeMesh:
                    cv2.circle(cv_img, self.eyeTrackThread.left_eye, int(self.eyeTrackThread.l_radius), (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.circle(cv_img, self.eyeTrackThread.right_eye, int(self.eyeTrackThread.r_radius), (0, 0, 255), 2, cv2.LINE_AA)

                print(result)
                #if self.tick:
                #    print("ok")
                cv2.putText(img=cv_img, text='OK', org=(480 - 30, 640 - 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3,
                            color=(52, 235, 52), thickness=3)

        # if pose detection is enabled
        if self.poseTrackThread.enabled:
            self.poseTrackThread.frame_count += 1

            if self.poseTrackThread.frame_count >= 2:
                self.videoThread.blockSignals(True)
                self.poseTrackThread.image = cv_img

            if self.poseTrackThread.results is not None:
                    self.mp_drawing.draw_landmarks(image=cv_img, landmark_list=self.poseTrackThread.results.pose_landmarks,
                                                   connections=mp.solutions.pose.POSE_CONNECTIONS,
                                                   landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(255, 255, 255),
                                                       thickness=3, circle_radius=3),
                                                   connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                                       color=(49, 125, 237),
                                                       thickness=2, circle_radius=2))

        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

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
