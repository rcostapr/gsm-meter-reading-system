# Only needed for access to command line arguments
import sys
# IP Address validation
from util.function import is_valid_ipaddress
# GUI
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QInputDialog, QLabel
# Designer
from gui.main import Ui_MainWindow


class GsmApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("GSM/GRPS Communication :: Energia Simples(2021)")

    def newText(self):
        self.lineEdit.setText("OK")


def main():

    # IP Address
    connection_ip = sys.argv[1]

    # command line arguments passed to the application
    app = QApplication(sys.argv)

    # create an instance
    window = GsmApp()

    window.lineEdit.setText(connection_ip)
    window.sendButton.clicked.connect(window.newText)

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
