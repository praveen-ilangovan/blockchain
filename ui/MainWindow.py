import sys

from PySide import QtGui
from PySide import QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Blockchain")
        self.resize(700, 400)

def main():
    app = QtGui.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec_()