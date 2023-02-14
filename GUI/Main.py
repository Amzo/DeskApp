from PyQt5 import QtGui
from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QMessageBox
from .Tabs import TabWidget


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Smart Unit Desk'
        self.left = 0
        self.top = 0
        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # openAction = QAction(QIcon('open.png'), '&Open', self)
        # openAction.setShortcut('Ctrl+O')
        # openAction.setStatusTip('Open movie')
        # openAction.triggered.connect(self.openFile)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        # fileMenu.addAction(newAction)
        # fileMenu.addAction(openAction)

        self.tab_widget = TabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.tabs.currentChanged.connect(self.onChange)
        self.show()

    # @pyqtSlot()
    def onChange(self, i):  # changed!
        if i == 0:
            self.tab_widget.camera.blockSignals(True)
        if i == 1:
            self.tab_widget.camera.blockSignals(False)
            self.tab_widget.camera.thread.blockSignals(False)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
