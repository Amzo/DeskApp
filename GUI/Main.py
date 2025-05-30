# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Amzo\Documents\DeskApp\Templates\DeskApp1.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1328, 820)
        MainWindow.setDockNestingEnabled(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.VideoWidget = QVideoWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VideoWidget.sizePolicy().hasHeightForWidth())
        self.VideoWidget.setSizePolicy(sizePolicy)
        self.VideoWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.VideoWidget.setObjectName("VideoWidget")
        self.gridLayout_2.addWidget(self.VideoWidget, 0, 0, 1, 2)
        self.VideoSlider = QtWidgets.QSlider(self.tab)
        self.VideoSlider.setOrientation(QtCore.Qt.Horizontal)
        self.VideoSlider.setObjectName("VideoSlider")
        self.gridLayout_2.addWidget(self.VideoSlider, 1, 0, 1, 1)
        self.durationLabel = QtWidgets.QLabel(self.tab)
        self.durationLabel.setObjectName("durationLabel")
        self.gridLayout_2.addWidget(self.durationLabel, 1, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.playButton = QtWidgets.QPushButton(self.tab)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_2.addWidget(self.playButton)
        self.pauseButton = QtWidgets.QPushButton(self.tab)
        self.pauseButton.setObjectName("pauseButton")
        self.horizontalLayout_2.addWidget(self.pauseButton)
        self.fullScreenBtn = QtWidgets.QPushButton(self.tab)
        self.fullScreenBtn.setObjectName("fullScreenBtn")
        self.horizontalLayout_2.addWidget(self.fullScreenBtn)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 2, 0, 1, 2)
        self.tabWidget.addTab(self.tab, "")
        self.tracking = QtWidgets.QWidget()
        self.tracking.setObjectName("tracking")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tracking)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lblCameraEye = QtWidgets.QLabel(self.tracking)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCameraEye.sizePolicy().hasHeightForWidth())
        self.lblCameraEye.setSizePolicy(sizePolicy)
        self.lblCameraEye.setFocusPolicy(QtCore.Qt.TabFocus)
        self.lblCameraEye.setAutoFillBackground(False)
        self.lblCameraEye.setStyleSheet("background-color: rgb(118, 112, 110);")
        self.lblCameraEye.setText("")
        self.lblCameraEye.setScaledContents(True)
        self.lblCameraEye.setObjectName("lblCameraEye")
        self.gridLayout_4.addWidget(self.lblCameraEye, 0, 0, 1, 1)
        self.lblCameraPose = QtWidgets.QLabel(self.tracking)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCameraPose.sizePolicy().hasHeightForWidth())
        self.lblCameraPose.setSizePolicy(sizePolicy)
        self.lblCameraPose.setFocusPolicy(QtCore.Qt.TabFocus)
        self.lblCameraPose.setAutoFillBackground(False)
        self.lblCameraPose.setStyleSheet("background-color: rgb(118, 112, 110);")
        self.lblCameraPose.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lblCameraPose.setText("")
        self.lblCameraPose.setScaledContents(True)
        self.lblCameraPose.setObjectName("lblCameraPose")
        self.gridLayout_4.addWidget(self.lblCameraPose, 0, 1, 1, 1)
        self.lblWrongPos = QtWidgets.QLabel(self.tracking)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblWrongPos.sizePolicy().hasHeightForWidth())
        self.lblWrongPos.setSizePolicy(sizePolicy)
        self.lblWrongPos.setFocusPolicy(QtCore.Qt.TabFocus)
        self.lblWrongPos.setAutoFillBackground(False)
        self.lblWrongPos.setStyleSheet("background-color: rgb(118, 112, 110);")
        self.lblWrongPos.setText("")
        self.lblWrongPos.setPixmap(QtGui.QPixmap("C:\\Users\\Amzo\\Documents\\DeskApp\\Templates\\../Images/incorrect.png"))
        self.lblWrongPos.setScaledContents(True)
        self.lblWrongPos.setObjectName("lblWrongPos")
        self.gridLayout_4.addWidget(self.lblWrongPos, 1, 1, 1, 1)
        self.lblCorrectPos = QtWidgets.QLabel(self.tracking)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCorrectPos.sizePolicy().hasHeightForWidth())
        self.lblCorrectPos.setSizePolicy(sizePolicy)
        self.lblCorrectPos.setFocusPolicy(QtCore.Qt.TabFocus)
        self.lblCorrectPos.setAutoFillBackground(False)
        self.lblCorrectPos.setStyleSheet("background-color: rgb(118, 112, 110);")
        self.lblCorrectPos.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lblCorrectPos.setText("")
        self.lblCorrectPos.setPixmap(QtGui.QPixmap("C:\\Users\\Amzo\\Documents\\DeskApp\\Templates\\../Images/correct.png"))
        self.lblCorrectPos.setScaledContents(True)
        self.lblCorrectPos.setObjectName("lblCorrectPos")
        self.gridLayout_4.addWidget(self.lblCorrectPos, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tracking, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1328, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtWidgets.QMenu(self.menuBar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menuBar)
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionConnect = QtWidgets.QAction(MainWindow)
        self.actionConnect.setObjectName("actionConnect")
        self.actionCalibrate = QtWidgets.QAction(MainWindow)
        self.actionCalibrate.setObjectName("actionCalibrate")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit_2 = QtWidgets.QAction(MainWindow)
        self.actionQuit_2.setObjectName("actionQuit_2")
        self.menuFile.addAction(self.actionConnect)
        self.menuFile.addAction(self.actionCalibrate)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit_2)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.durationLabel.setText(_translate("MainWindow", "0:00/0:00"))
        self.playButton.setText(_translate("MainWindow", "Play"))
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.fullScreenBtn.setText(_translate("MainWindow", "Fullscreen"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Demo"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tracking), _translate("MainWindow", "Tracking"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "History"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionConnect.setText(_translate("MainWindow", "Connect"))
        self.actionCalibrate.setText(_translate("MainWindow", "Calibrate"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit_2.setText(_translate("MainWindow", "Quit"))
from PyQt5.QtMultimediaWidgets import QVideoWidget
