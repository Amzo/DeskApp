import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, \
    QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from .VideoPlayer import VideoWindow
from .Camera import CameraWindow


class TabWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        #self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Demo")
        self.tabs.addTab(self.tab2, "Posture")

        # Create first tab
        self.tab1.layout = QHBoxLayout(self)
        self.VideoPlayer = VideoWindow()
        self.tab1.layout.addWidget(self.VideoPlayer)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QHBoxLayout(self)
        self.camera = CameraWindow()
        self.tab2.layout.addWidget(self.camera)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
