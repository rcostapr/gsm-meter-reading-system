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
        MainWindow.resize(1011, 803)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(1011, 803))
        MainWindow.setMaximumSize(QSize(1011, 803))
        MainWindow.setFocusPolicy(Qt.TabFocus)
        icon = QIcon()
        icon.addFile(u"../../../.designer/backup/image/favicon.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.actionSIM800 = QAction(MainWindow)
        self.actionSIM800.setObjectName(u"actionSIM800")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.sendButton = QPushButton(self.centralwidget)
        self.sendButton.setObjectName(u"sendButton")
        self.sendButton.setGeometry(QRect(900, 560, 101, 40))
        self.lstLog = QListView(self.centralwidget)
        self.lstLog.setObjectName(u"lstLog")
        self.lstLog.setGeometry(QRect(550, 30, 451, 511))
        self.txtNumber = QLineEdit(self.centralwidget)
        self.txtNumber.setObjectName(u"txtNumber")
        self.txtNumber.setGeometry(QRect(550, 560, 341, 41))
        self.txtMessage = QPlainTextEdit(self.centralwidget)
        self.txtMessage.setObjectName(u"txtMessage")
        self.txtMessage.setGeometry(QRect(550, 610, 451, 131))
        self.lstMsg = QListView(self.centralwidget)
        self.lstMsg.setObjectName(u"lstMsg")
        self.lstMsg.setGeometry(QRect(10, 30, 531, 511))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1011, 22))
        self.menuGSM = QMenu(self.menubar)
        self.menuGSM.setObjectName(u"menuGSM")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.txtNumber, self.sendButton)
        QWidget.setTabOrder(self.sendButton, self.lstLog)

        self.menubar.addAction(self.menuGSM.menuAction())
        self.menuGSM.addAction(self.actionSIM800)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        MainWindow.setToolTip(QCoreApplication.translate("MainWindow", u"GSM GPRS Communications", None))
#endif // QT_CONFIG(tooltip)
        self.actionSIM800.setText(QCoreApplication.translate("MainWindow", u"SIM800", None))
        self.sendButton.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.txtNumber.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Phone Number", None))
        self.txtMessage.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Message to send", None))
        self.menuGSM.setTitle(QCoreApplication.translate("MainWindow", u"Mobile", None))
    # retranslateUi

