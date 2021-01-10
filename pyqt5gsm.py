import sys
import time
from util.function import is_valid_ipaddress
# GUI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QInputDialog, QLabel
import gui.main as mgui


class GsmApp(QtWidgets.QMainWindow, mgui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(GsmApp, self).__init__(parent)
        self.setupUi(self)

    def newText(self):
        self.lineEdit.setText("OK")


def main():

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

    connection_ip = sys.argv[1]

    app = QApplication(sys.argv)
    form = GsmApp()
    form.lineEdit.setText(connection_ip)
    form.sendButton.clicked.connect(form.newText)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
