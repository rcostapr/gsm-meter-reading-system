# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(898, 625)
        self.actionSIM800 = QAction(MainWindow)
        self.actionSIM800.setObjectName(u"actionSIM800")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(340, 0, 211, 561))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout.addWidget(self.lineEdit)

        self.sendButton = QPushButton(self.verticalLayoutWidget)
        self.sendButton.setObjectName(u"sendButton")

        self.verticalLayout.addWidget(self.sendButton)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setGeometry(QRect(610, 0, 300, 23))
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(8)
        self.checkBox = QCheckBox(self.splitter)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setCheckable(False)
        self.splitter.addWidget(self.checkBox)
        self.labelIpAddress = QLabel(self.splitter)
        self.labelIpAddress.setObjectName(u"labelIpAddress")
        self.splitter.addWidget(self.labelIpAddress)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 898, 22))
        self.menuGSM = QMenu(self.menubar)
        self.menuGSM.setObjectName(u"menuGSM")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuGSM.menuAction())
        self.menuGSM.addAction(self.actionSIM800)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSIM800.setText(QCoreApplication.translate("MainWindow", u"SIM800", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Message to send", None))
        self.sendButton.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"Connected", None))
        self.labelIpAddress.setText(QCoreApplication.translate("MainWindow", u"IP Address", None))
        self.menuGSM.setTitle(QCoreApplication.translate("MainWindow", u"Mobile", None))
    # retranslateUi

