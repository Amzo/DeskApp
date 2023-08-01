import math
import sys
import time

import cv2
import mediapipe as mp
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from GUI import Main
from GUI import VideoPlayer
from GUI.Camera import VideoThread
from Lib.Connection import ConnectPi
from Lib.EyeMesh import EyeMesh, EyePosition
from Lib.PoseDetection import PoseDetection, PosePosition


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_variables()
        self.setup_ui()
        self.setup_connections()
        self.setup_camera_and_video()
        self.setup_eye_tracking()
        self.setup_pose_detection()

    def init_variables(self):
        self.connection = None
        self.everyFrameParse = 3
        self.setAttribute(Qt.WA_NativeWindow, True)

        self.sc = None
        self.added = False
        self.badPostureCount = 0
        self.goodPostureCount = 0
        self.GResults = []
        self.BResults = []
        self.minute = 0
        self.distanceResults = []
        self.starttime = None
        self.postureStartTime = time.time()
        self.calibrationRunning = False
        self.connected = False
        self.rightDistance = 64

        self.display_width = 640
        self.display_height = 360

        self.fullScreenMode = False
        self.frame_count = 0
        self.eyePos = EyePosition()
        self.eyeMesh = True

        self.posePos = PosePosition()
        self.poseMesh = True

    def setup_ui(self):
        self.ui = Main.Ui_MainWindow()
        self.ui.setupUi(self)

    def setup_connections(self):
        self.ui.actionConnect.triggered.connect(self.connectToPi)
        self.ui.actionCalibrate.triggered.connect(self.calibrate)
        self.ui.playButton.clicked.connect(self.play)
        self.ui.pauseButton.clicked.connect(self.pause)
        self.ui.fullScreenBtn.clicked.connect(self.fullscreen)
        self.ui.tabWidget.currentChanged.connect(self.onChange)

    def setup_camera_and_video(self):
        self.mediaPlayer = VideoPlayer.VideoWindow(self.ui.VideoWidget)
        self.mediaPlayer.playback_slider_signal.connect(self.slider_update)
        self.mediaPlayer.playback_duration_signal.connect(self.video_duration)

        self.videoThread = VideoThread()
        self.videoThread.change_pixmap_signal.connect(self.update_image)
        self.videoThread.start()

    def setup_eye_tracking(self):
        self.personPresent = False
        self.eyeTrackThread = EyeMesh()
        self.eyeTrackThread.eyes_detected_signal.connect(self.update_eye_detection_status)  # Connect the signal to the slot
        self.eyeTrackThread.start()
        self.eyeTrackThread.enabled = True

    def setup_pose_detection(self):
        self.mp_drawing = mp.solutions.drawing_utils

        self.poseTrackThread = PoseDetection()
        self.poseTrackThread.start()

        self.poseTrackThread.enabled = True

    def setTabVisibility(self, index, visible):
        for i in range(self.ui.tabWidget.count()):
            if i != index:
                self.ui.tabWidget.tabBar().setTabVisible(i, visible)

        if not visible:
            self.ui.tabWidget.tabBar().hide()  # hide the tab bar when in full-screen mode
        else:
            self.ui.tabWidget.tabBar().show()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = QApplication.keyboardModifiers()

        if modifiers == (
                Qt.ControlModifier | Qt.AltModifier) and (
                key == Qt.Key_F and Qt.Key_P) and self.windowState() & Qt.WindowFullScreen:
            self.fullScreenMode = False
            # The secret key combination Ctrl+Alt+F is pressed
            if self.windowState() & Qt.WindowFullScreen:  # if already in full screen
                self.setWindowState(self.windowState() & ~Qt.WindowFullScreen)  # exit full screen
                self.setTabVisibility(self.ui.tabWidget.indexOf(self.ui.tracking), True)
                self.menuBar().show()
        elif key == Qt.Key_F and self.ui.tabWidget.currentIndex() == self.ui.tabWidget.indexOf(self.ui.tracking):
            # The key F is pressed when the 'tracking' tab is selected
            if not (self.windowState() & Qt.WindowFullScreen):  # if not already in full screen
                self.fullScreenMode = True
                self.setWindowState(self.windowState() | Qt.WindowFullScreen)  # enter full screen
                self.setTabVisibility(self.ui.tabWidget.indexOf(self.ui.tracking), False)
                self.menuBar().hide()
        elif key == Qt.Key_Escape and self.windowState() & Qt.WindowFullScreen:
            # The Escape key is pressed when in full screen mode. Ignore it.
            return
        else:
            # Any other key or key combination is pressed
            super(MainWindow, self).keyPressEvent(event)

    def closeEvent(self, event):
        if not self.fullScreenMode:  # If not in full screen mode
            reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.videoThread.stop()
                self.eyeTrackThread.stop()

                event.accept()
            else:
                event.ignore()
        else:  # If in full screen mode
            event.ignore()  # Ignore the close event

    @pyqtSlot(bool)
    def update_eye_detection_status(self, is_detected):
        if is_detected and not self.personPresent:
            self.personPresent = True
            print("Eyes detected.")
            self.calibrate()
        else:
            self.personPresent = False
            print("Eyes not detected.")

    def calibrate(self):
        calibrate = QMessageBox()
        calibrate.setWindowTitle("Calibration")
        calibrate.setText("To Calibrate, sit in the upright position, and align eyes to the center of the screen "
                          "until the green tick appears. "
                          ""
                          ""
                          "Once ready click Okay and maintain for 5 seconds")

        calibrate.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        calibrate.buttonClicked.connect(self.calibrateClicked)

        calibrate.exec_()

    def calibrateClicked(self, i):
        if i.text() == "OK" and not self.calibrationRunning:
            print("Running Calibration")
            self.starttime = time.time()
            self.distanceResults = []
            self.calibrationRunning = True
        elif self.calibrationRunning:
            QMessageBox.about(self, "Error", "Calibration already running")

    def connectToPi(self):
        print("Running connect to Pi")
        self.connection = ConnectPi("10.42.0.1", 1883)
        self.connection.connect_to_pi()
        print("Connecting to Pi")

    def toggleEyeTrack(self):
        self.eyeTrackThread.enabled = not self.eyeTrackThread.enabled

    def toggleEyeMesh(self):
        self.eyeMesh = not self.eyeMesh

    def togglePoseTrack(self):
        self.poseTrackThread.enabled = not self.poseTrackThread.enabled

    def togglePoseMesh(self):
        self.poseMesh = not self.poseMesh

    def play(self):
        self.ui.playButton.setStyleSheet("background-color : lightblue")
        self.ui.pauseButton.setStyleSheet("background-color : lightgrey")
        self.mediaPlayer.mediaPlayer.play()

    def fullscreen(self):
        self.ui.VideoWidget.setFullScreen(True)
        # self.mediaPlayer.showFullScreen()

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

        # print(timex)
        try:
            if self.connection.connected:
                if timex == "053":
                    print("sending message")
                    self.connection.send_message("pink")
                elif timex == "208":
                    print("Sending message")
                    self.connection.send_message("green")
                elif timex == "225":
                    print("sending message")
                    self.connection.send_message("blue")
                elif timex == "258":
                    self.connection.send_message("orange")
                elif timex == "103" or timex == "221" or timex == "238" or timex == "312":
                    self.connection.send_message("off")
        except AttributeError:
            pass

    @staticmethod
    def convert_seconds(seconds):
        hours = math.floor(seconds / 3600)
        minutes = math.floor((seconds - (hours * 3600)) / 60)
        secs = seconds - (hours * 3600) - (minutes * 60)

        return minutes, secs

    def video_duration(self, duration):
        self.ui.VideoSlider.setRange(0, duration)

    def onChange(self, i):  # changed!
        print(i)
        if i == 0:
            self.play()
            # self.tab_widget.camera.blockSignals(True)
            # self.tab_widget.camera.videoThread.pause = True
        if i == 1:
            self.pause()
            # self.tab_widget.camera.blockSignals(False)
            # self.tab_widget.camera.videoThread.pause = False
            # self.tab_widget.camera.thread.blockSignals(False)

    def draw_symbol(self, center, is_tick, color, thickness):
        offset = 50  # adjust as needed for the size of the tick or cross
        if is_tick:
            # For a tick mark, we will draw two lines
            # First line (starts from 2/3 down the left side of the cross, goes to the bottom center)
            cv2.line(self.eyeTrackThread.image,
                     (center[0] - offset // 2, center[1] - offset // 3),
                     (center[0], center[1] + offset // 2), color, thickness)
            # Second line (starts from the bottom center, goes to the top right corner)
            cv2.line(self.eyeTrackThread.image,
                     (center[0], center[1] + offset // 2),
                     (center[0] + offset // 2, center[1] - offset // 2), color, thickness)
        else:
            cv2.line(self.eyeTrackThread.image, (center[0] - offset, center[1] - offset),
                     (center[0] + offset, center[1] + offset), color, thickness)
            cv2.line(self.eyeTrackThread.image, (center[0] + offset, center[1] - offset),
                     (center[0] - offset, center[1] + offset), color, thickness)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        center_x = cv_img.shape[1] // 2
        center_y = cv_img.shape[0] // 2

        pose_img = None

        self.frame_count += 1

        if self.eyeTrackThread.distance is not None:
            cv2.putText(cv_img,
                        f'{math.ceil(self.eyeTrackThread.distance)} cm',
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA)

        if self.frame_count >= self.everyFrameParse:
            self.eyeTrackThread.image_signal.emit(cv_img)
            self.eyeTrackThread.perform_calculations()


        if self.calibrationRunning:
            elapsed_time = time.time() - self.starttime

            if elapsed_time < 5:
                text = f'{abs(math.ceil(5 - elapsed_time))}'
            elif elapsed_time < 8:
                text = 'Complete'
            else:
                self.calibrationRunning = False
                self.rightDistance = sum(self.distanceResults) / len(self.distanceResults)
                return

            font_scale = 2
            thickness = 8
            font = cv2.FONT_HERSHEY_SIMPLEX

            # Get the width and height of the text box
            text_width, text_height = cv2.getTextSize(text, font, font_scale, thickness)[0]
            x = (self.eyeTrackThread.image.shape[1] - text_width) // 2
            y = (self.eyeTrackThread.image.shape[0] + text_height) // 2


            # Draw the text on the image
            cv2.putText(self.eyeTrackThread.image,
                        text,
                        (x, y),
                        font,
                        font_scale,
                        (0, 255, 0),
                        thickness,
                        cv2.LINE_AA)

        if self.eyeTrackThread.result:
            if self.calibrationRunning and elapsed_time < 5:
                self.distanceResults.append(math.ceil(self.eyeTrackThread.distance))

            self.draw_symbol((center_x, center_y), True, (52, 255, 52), 2)
        else:
            self.draw_symbol((center_x, center_y), False, (0, 0, 255), 2)

        if self.calibrationRunning and time.time() - self.starttime > 7:  # 5 seconds for calibration, 2 seconds for
            # 'Complete' message
            self.calibrationRunning = False
            self.rightDistance = sum(self.distanceResults) / len(self.distanceResults)
            print(self.rightDistance)

        # if pose detection is enabled
        if self.poseTrackThread.enabled:
            pose_img = cv_img.copy()

            if self.frame_count >= self.everyFrameParse:
                self.poseTrackThread.image_signal.emit(cv_img)

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

                try:
                    if (self.rightDistance - 4) < math.ceil(self.eyeTrackThread.distance) < (
                            self.rightDistance + 4):  # or result
                        self.goodPostureCount += 1
                        cv2.line(pose_img, (630, 310), (610, 340), (52, 255, 52), 2)
                        cv2.line(pose_img, (610, 340), (600, 325), (52, 255, 52), 2)
                    else:
                        self.badPostureCount += 1
                        cv2.line(pose_img, (630, 310), (610, 340), (0, 0, 255), 2)
                        cv2.line(pose_img, (610, 310), (630, 340), (0, 0, 255), 2)
                except TypeError:
                    pass

        if self.eyeTrackThread.image is not None:
            eye_img = self.convert_cv_qt(self.eyeTrackThread.image)
            self.ui.lblCameraEye.setPixmap(eye_img)
        else:
            qt_img = self.convert_cv_qt(cv_img)
            self.ui.lblCameraEye.setPixmap(qt_img)

        if pose_img is not None:
            pose_img = self.convert_cv_qt(pose_img)
            self.ui.lblCameraPose.setPixmap(pose_img)
        else:
            qt_img = self.convert_cv_qt(cv_img)
            self.ui.lblCameraPose.setPixmap(qt_img)

        if self.frame_count >= self.everyFrameParse:
            self.frame_count = 0

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
