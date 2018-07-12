import sys

from PySide import QtGui

# Local imports
from . import widgets

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Blockchain")
        self.resize(700, 400)

        # Tabs
        self.__tabWidget = QtGui.QTabWidget()
        self.__tabWidget.setTabShape(QtGui.QTabWidget.Rounded)

        # Add widgets to the tab
        self.__generateWalletWidget = widgets.GenerateWalletWidget()
        self.__makeTransactionWidget = widgets.MakeTransactionWidget()
        self.__transactionToCommitWidget = widgets.TransactionsToCommitWidget()

        self.__tabWidget.addTab(self.__generateWalletWidget, "Generate Wallet")
        self.__tabWidget.addTab(self.__makeTransactionWidget, "Make Transaction")
        self.__tabWidget.addTab(self.__transactionToCommitWidget,
                                "View Pending Transactions")

        self.setCentralWidget(self.__tabWidget)

        self.__tabWidget.currentChanged.connect(self.tabChanged)

    def tabChanged(self, index):
        self.__tabWidget.widget(index).refresh()

def launch_ui():
    app = QtGui.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec_()