import sys
import json
import requests
# IP Address validation
from util.function import is_valid_ipaddress
# GUI
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QInputDialog, QLabel, QToolBar, QAction, QStyle
# Designer
from gui.main import Ui_MainWindow
# SSH
from paramiko import SSHClient, AutoAddPolicy


class GsmApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # IP Address
        self.ip = QApplication.arguments()[1]
        self.setupUi(self)
        self.buildObjects()
        self.setIcons()
        self.setActions()
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')

    def buildObjects(self):
        # Build ToolBar
        toolbar = QToolBar("GSM")
        self.addToolBar(toolbar)
        # Build ToolBar Buttons
        button_action = QAction(self.getIcon("btn1"), "Get Messages", self)
        button_action.setStatusTip("Messages on the phone")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(False)
        toolbar.addAction(button_action)

        self.btn2 = QAction(self.getIcon("btn2F"), "Connection", self)
        self.btn2.setStatusTip("Set Connection")
        self.btn2.triggered.connect(self.makeConnection)
        self.btn2.setCheckable(True)
        toolbar.addAction(self.btn2)

    def onMyToolBarButtonClick(self):
        self.statusbar.showMessage('btn was clicked')
        print("click")

    def makeConnection(self, state):
        if state:
            self.btn2.setIcon(self.getIcon("btn2T"))
            self.statusbar.showMessage('Connecting...')
            # TODO: Connecting with Raspeberry
            log = QtGui.QStandardItemModel()
            self.lstLog.setModel(log)
            item = QtGui.QStandardItem("Connecting...")
            log.appendRow(item)

            # IP Address
            ip = self.ip

        if not state:
            self.btn2.setIcon(self.getIcon("btn2F"))
            self.statusbar.showMessage('Disconnecting')

    def sshConnection(self, state):
        # IP Address
        ip = QApplication.arguments()[1]
        # JSON file
        f = open('sftp.json', "r")
        # Reading from file
        data = json.loads(f.read())

        # Closing file
        f.close()

        client = SSHClient()
        client.load_system_host_keys()
        # client.load_host_keys('~/.ssh/known_hosts')
        client.set_missing_host_key_policy(AutoAddPolicy())

        # client.connect(ip, username=data["name"], key_filename=data["privateKeyPath"])

        # client.look_for_keys(True)
        client.connect(ip, port=data["port"], username=data["username"])

        stdin, stdout, stderr = client.exec_command('ls -l')

        # Print output of command. Will wait for command to finish.
        # print(f'STDOUT: {stdout.read().decode("utf8")}')
        # print(f'STDERR: {stderr.read().decode("utf8")}')

        # Get return code from command (0 is default for success)
        # print(f'Return code: {stdout.channel.recv_exit_status()}')

        # Because they are file objects, they need to be closed
        stdin.close()
        stdout.close()
        stderr.close()

        # Close the client itself
        client.close()

    def setActions(self):
        self.sendButton.clicked.connect(self.sendSms)

    def setIcons(self):
        self.setWindowIcon(self.getIcon("appIcon"))
        self.sendButton.setIcon(self.getIcon("sendButton"))

    def getIcon(self, objImg):
        imgPath = "gui/image/"
        icoPath = "gui/image/icons/icons/"
        switcher = {
            "appIcon": imgPath + "favicon.png",
            "sendButton": icoPath + "mail-send.png",
            "btn1": icoPath + "mail-send-receive.png",
            "btn2T": icoPath + "plug-connect.png",
            "btn2F": icoPath + "plug-disconnect.png",
            "btn2": icoPath + "plug-disconnect-prohibition.png",
        }
        img = switcher.get(objImg, imgPath + "favicon.png")
        imgIcon = QtGui.QIcon(img)
        return imgIcon

    def sendSms(self):
        log = QtGui.QStandardItemModel()
        self.lstLog.setModel(log)

        payload = {
            'number': self.txtNumber.text(),
            'message': self.txtMessage.toPlainText()
        }

        item = QtGui.QStandardItem("Send SMS to... " + self.txtNumber.text())
        log.appendRow(item)

        # +351938370555
        # Sended by python
        # data = 'CONTENT_TYPE': 'application/x-www-form-urlencoded'
        # json = 'CONTENT_TYPE': 'application/json'
        url = 'http://{}/phone/sendsms'.format(self.ip)
        r = requests.post(url, json=payload)

        item = QtGui.QStandardItem(r.text)
        log.appendRow(item)
        print(r.text)

        # self.txtMsg.setText("OK")


def main():

    # IP Address
    connection_ip = sys.argv[1]

    # command line arguments passed to the application
    app = QApplication(sys.argv)

    # create an instance
    window = GsmApp()

    window.setWindowTitle("GSM GRPS Communication :: " + connection_ip)

    # Center Window on Screen
    screen = QtWidgets.QDesktopWidget().screenGeometry()
    size = window.geometry()
    x_center = (screen.width() - size.width()) / 2
    y_center = (screen.height() - size.height()) / 2
    size.setTop(y_center)
    size.setLeft(x_center)
    window.setGeometry(size)

    # Show Main Window
    window.show()

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: sh {} <ip_address>".format(sys.argv[0]))
        sys.exit("Wrong Parameters")

    if not is_valid_ipaddress(sys.argv[1].strip()):
        sys.exit("Invalid IP Address: {}".format(sys.argv[1].strip()))

    # Catch flags
    if len(sys.argv) > 2:
        for flag in sys.argv[2:]:
            if flag == '--detach':
                print("Found: " + flag)
    main()
