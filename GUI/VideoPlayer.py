import sys

from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction


class VideoWindow(QWidget):
    playback_slider_signal = pyqtSignal(int)
    playback_duration_signal = pyqtSignal(int)

    def __init__(self, widget):
        super(QWidget, self).__init__()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(widget)
        self.mediaPlayer.stateChanged.connect(self.stateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile('C:\\Users\\Amzo\\Downloads\\file_example_MP4_1920_18MG.mp4')))
        # self.playButton.setEnabled(True)

        # self.showMaximized()

    def positionChanged(self, position):
        self.playback_slider_signal.emit(position)

    def durationChanged(self, duration):
        self.playback_duration_signal.emit(duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    # for repeating
    def stateChanged(self):
        if self.mediaPlayer.state() == 0:
            self.mediaPlayer.play()
