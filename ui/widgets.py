# PySide imports
from PySide import QtGui
from PySide import QtCore

# Local imports
from ..src import database
from ..src.wallet import Wallet

MIN_WIDTH = 150
MIN_HEIGHT = 50

##############################################################################
#
# UTILITY WIDGETS
#
##############################################################################

class SetPasswordDialog(QtGui.QDialog):
    """ A simple widget to validate and set a password.
        
    """
    def __init__(self, parent=None):
        super(SetPasswordDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Set a new password")
        self.resize(500, 70)

        self.__enterLabel = QtGui.QLabel('Enter a password : ')
        self.__enterEdit = self.__create_password_edit()
        self.__confirmLabel = QtGui.QLabel('Confirm password : ')
        self.__confirmEdit = self.__create_password_edit()

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton("Set Password", QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(self.validatePassword)
        buttonBox.rejected.connect(self.reject)

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(self.__enterLabel, 0,0,1,1)
        gridLayout.addWidget(self.__enterEdit, 0,1,1,1)
        gridLayout.addWidget(self.__confirmLabel, 1,0,1,1)
        gridLayout.addWidget(self.__confirmEdit, 1,1,1,1)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

    def __create_password_edit(self):
        echoMode = QtGui.QLineEdit.Password
        ledit = QtGui.QLineEdit()
        ledit.setEchoMode(echoMode)
        return ledit

    def validatePassword(self):
        password = self.getPassword()

        if not password:
            return

        if password == str(self.__confirmEdit.text()):
            self.accept()
        else:
            self.__enterEdit.clear()
            self.__confirmEdit.clear()
            QtGui.QMessageBox.critical(self, "Failed",
                                       "Password did not match")

    def getPassword(self):
        return str(self.__enterEdit.text())

class KeyDisplayWidget(QtGui.QWidget):
    """ A simple widget to display the RSA key.
        
    """
    def __init__(self, label, parent=None):
        super(KeyDisplayWidget, self).__init__(parent)

        self.__label = QtGui.QLabel("%s :" %(label))
        self.__textBox = QtGui.QTextEdit()
        self.__textBox.setReadOnly(True)
        self.__textBox.setMinimumHeight(80)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.__label)
        mainLayout.addWidget(self.__textBox)

        self.setLayout(mainLayout)

    def setText(self, text):
        self.__textBox.setText(text)

    def clearText(self):
        self.__textBox.clear()

##############################################################################
#
# MAIN WIDGETS
#
##############################################################################
class GenerateWalletWidget(QtGui.QWidget):
    """ Widget to generate a new wallet.

    Expects the user to enter a name. The name is checked against
    the database to make sure it is unique. The user should also
    set a password to the account.

    The details are passed over to the Wallets module which sets up
    a new account and also creates a RSA public and private keys.
    The information is then stored in the database. The private key 
    is encrypted with the password provided by the user before
    storing it in the database. Only the user with this password can
    decrypt and access the private key.
    """
    def __init__(self, parent=None):
        super(GenerateWalletWidget, self).__init__(parent)        

        # Enter a name
        self.__nameLabel = QtGui.QLabel("  Name       :")
        self.__nameEdit = QtGui.QLineEdit()
        self.__nameEdit.setMinimumWidth(MIN_WIDTH)
        self.__nameEdit.setMinimumHeight(MIN_HEIGHT)
        self.__generateButton = QtGui.QPushButton("Generate")
        self.__generateButton.setMinimumWidth(MIN_WIDTH)
        self.__generateButton.setMinimumHeight(MIN_HEIGHT)
        self.__refreshButton = QtGui.QPushButton("Refresh")
        self.__refreshButton.setMinimumWidth(MIN_WIDTH)
        self.__refreshButton.setMinimumHeight(MIN_HEIGHT)
        # TODO : Change the refresh text with an icon.

        # widgets to display RSA keys
        self.__pubKeyBox = KeyDisplayWidget("Public Key ")
        self.__pvtKeyBox = KeyDisplayWidget("Private Key")

        registerLayout = QtGui.QHBoxLayout()
        registerLayout.addWidget(self.__nameLabel)
        registerLayout.addWidget(self.__nameEdit)
        registerLayout.addWidget(self.__generateButton)
        registerLayout.addWidget(self.__refreshButton)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(registerLayout)
        mainLayout.addStretch(0)
        mainLayout.addWidget(self.__pubKeyBox)
        mainLayout.addStretch(0)
        mainLayout.addWidget(self.__pvtKeyBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

        self.__generateButton.clicked.connect(self.generate)
        self.__refreshButton.clicked.connect(self.refresh)

    def generate(self):
        name = str(self.__nameEdit.text())
        if not name:
            QtGui.QMessageBox.critical(self, "No name", 
                                       "Please enter a name.")
            return

        if not database.is_unique_name(name):
            QtGui.QMessageBox.critical(self, "Username already exists", 
                                       "Please select a unique name.")
            return

        # Password
        dialog = SetPasswordDialog(self)
        if dialog.exec_():
            password = dialog.getPassword()
        else:
            return

        wallet = Wallet.generate(name, password)
        if not wallet:
            QtGui.QMessageBox.critical(self, "Failed", 
                                       "Failed to generate a wallet")
            return

        # populate the key boxes
        self.__pubKeyBox.setText(wallet.get_serialized_public_key())
        self.__pvtKeyBox.setText(wallet.get_serialized_private_key())

    def refresh(self):
        self.__nameEdit.clear()
        self.__pubKeyBox.clearText()
        self.__pvtKeyBox.clearText()