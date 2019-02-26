# PySide imports
from PySide import QtGui
from PySide import QtCore

# Local imports
from ..src import database
from ..src.wallet import Wallet
from ..src import transaction
from ..src import mining

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

class GetPasswordDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(GetPasswordDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Password")
        self.resize(500, 70)

        self.__enterLabel = QtGui.QLabel('Enter your password : ')
        self.__enterEdit = self.__create_password_edit()

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton("OK", QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(self.__enterLabel, 0,0,1,1)
        gridLayout.addWidget(self.__enterEdit, 0,1,1,1)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

    def __create_password_edit(self):
        echoMode = QtGui.QLineEdit.Password
        ledit = QtGui.QLineEdit()
        ledit.setEchoMode(echoMode)
        return ledit

    def get_password(self):
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

class UserComboBox(QtGui.QWidget):
    """ A drop down box to list all the available users
    in the database.
    """
    def __init__(self, label, parent=None):
        super(UserComboBox, self).__init__(parent)

        self.__label = QtGui.QLabel("%s :" %(label))
        self.__cbox = QtGui.QComboBox()
        self.__cbox.setMinimumWidth(MIN_WIDTH)
        self.__cbox.setMinimumHeight(MIN_HEIGHT)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.__label)
        mainLayout.addWidget(self.__cbox)

        self.setLayout(mainLayout)

    def populate(self, users):
        self.__cbox.clear()
        for user in users:
            self.__cbox.addItem(user)

    def get_user(self):
        return str(self.__cbox.currentText())

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

class MakeTransactionWidget(QtGui.QWidget):
    """ Widget to make a transaction

    Choose the sender, receiver and enter the amount to
    be transfered. Then click 'Make transaction' button
    to initiate a transaction. You will be prompted to
    enter the password. This password is used to decrypt
    the RSA private key of the sender which is then used to
    sign the transaction.

    The signed transaction is then verified by the block module
    to validate the transaction. If it is verified then the
    transaction is added to the pending queue.
    """
    def __init__(self, parent=None):
        super(MakeTransactionWidget, self).__init__(parent)

        self.__senderBox   = UserComboBox("Sender   ")
        self.__receiverBox = UserComboBox("Receiver ")
        self.__amountLabel = QtGui.QLabel(" Amount   :")
        self.__amountEdit  = QtGui.QDoubleSpinBox()
        self.__amountEdit.setMinimum(0.01)
        self.__amountEdit.setSingleStep(1.0)
        self.__amountEdit.setMinimumWidth(MIN_WIDTH)
        self.__amountEdit.setMinimumHeight(MIN_HEIGHT)
        self.__makeTransactionButton = QtGui.QPushButton("Make Transaction")
        self.__makeTransactionButton.setMinimumHeight(80)

        amountLayout = QtGui.QHBoxLayout()
        amountLayout.addWidget(self.__amountLabel)
        amountLayout.addWidget(self.__amountEdit)
        amountLayout.addStretch(0)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.__senderBox,
                                alignment = QtCore.Qt.AlignLeft)
        mainLayout.addStretch(0)
        mainLayout.addWidget(self.__receiverBox,
                                alignment = QtCore.Qt.AlignLeft)
        mainLayout.addStretch(0)
        mainLayout.addLayout(amountLayout)
        mainLayout.addStretch(0)
        mainLayout.addWidget(self.__makeTransactionButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

        self.__makeTransactionButton.clicked.connect(self.makeTransaction)

    def populateUsers(self):
        users = [""]
        users.extend(database.get_wallet_holders())

        self.__senderBox.populate(users)
        self.__receiverBox.populate(users)

    def makeTransaction(self):
        sender = str(self.__senderBox.get_user())
        if not sender:
            QtGui.QMessageBox.critical(self, "Invalid input",
                                       "Please choose the sender")
            return

        receiver = str(self.__receiverBox.get_user())
        if not receiver:
            QtGui.QMessageBox.critical(self, "Invalid input",
                                       "Please choose the receiver")
            return

        if sender == receiver:
            QtGui.QMessageBox.critical(self, "Invalid input",
                        "Sender and receiver cannot be the same.")
            return

        amount = self.__amountEdit.value()
        if amount < 0.01:
            QtGui.QMessageBox.critical(self, "Invalid input",
                            "Please specify an amount more than 0.01")
            return

        dialog = GetPasswordDialog()
        if dialog.exec_():
            password = dialog.get_password()
            submitted = transaction.submit_transaction(sender, receiver,
                amount, password)
            if submitted:
                QtGui.QMessageBox.information(self, "Success",
                    " Transaction has been successfully submitted \
                    to a queue. Soon this will be verified by a miner \
                    and added to a block.")
            else:
                QtGui.QMessageBox.critical(self, "Failed",
                    " Transaction failed. Please check the password. \
                    For more details refer to the log. ")

    def refresh(self):
        self.populateUsers()
        self.__amountEdit.setValue(0.01)

class DataDisplayWidget(QtGui.QTableWidget):
    def __init__(self, columns, headerLables, keys, parent=None):
        super(DataDisplayWidget, self).__init__(parent)
        self.setColumnCount(columns)
        self.__headerLabels = headerLables
        self.__keys = keys

    def populate(self, data):
        self.clearContents()
        self.setHorizontalHeaderLabels(self.__headerLabels)

        for index, detail in enumerate(data):
            if index >= self.rowCount():
                self.insertRow(index)
            for i, key in enumerate(self.__keys):
                self.setItem(index, i, self.__getItem(detail[key]))

    def __getItem(self, text):
        item = QtGui.QTableWidgetItem()
        item.setText(str(text))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        return item

class TransactionsToCommitWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TransactionsToCommitWidget, self).__init__(parent)

        # Reads from transactions.json and passes it over to blockviewwidget to populate
        """
        structure = [{'sender' : name,
                      'receiver' : name,
                      'amount' : number,
                      'timestamp' : datetime
                     },
                    ...]
        """
        self.__currentBlock = DataDisplayWidget(4,
            ['Sender', 'Receiver', 'Amount', 'Time created'],
            ['sender', 'receiver', 'amount', 'submitted_time'])
        self.__mineButton = QtGui.QPushButton("Mine")
        self.__mineButton.setMinimumWidth(MIN_WIDTH)
        self.__mineButton.setMinimumHeight(MIN_HEIGHT)
        self.__refreshButton = QtGui.QPushButton("Refresh")
        self.__refreshButton.setMinimumWidth(MIN_WIDTH)
        self.__refreshButton.setMinimumHeight(MIN_HEIGHT)

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.__mineButton)
        buttonLayout.addWidget(self.__refreshButton)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.__currentBlock)
        mainLayout.addStretch(0)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

        self.__mining = mining.Mining()
        self.__mineButton.clicked.connect(self.__mining.mine)
        self.__refreshButton.clicked.connect(self.populateBlock)

    def populateBlock(self):
        transactions = transaction.get_pending_transactions()
        self.__currentBlock.populate(transactions)

    def refresh(self):
        self.populateBlock()

class BlockchainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BlockchainWidget, self).__init__(parent)

        # A table widget to view all the blocks in the
        # blockchain
        # Block name, number of transactions, transacted amount, timestamp
        self.__blockwidget = DataDisplayWidget(4,
            ['Name', 'Count', 'Total amount', 'Time created'],
            ['name', 'num_of_transactions', 'transacted_amount', 'added_time'])
        self.__transactionWidget = DataDisplayWidget(5,
            ['Sender', 'Receiver', 'Amount', 'Time created', 'Time verified'],
            ['sender', 'receiver', 'amount', 'submitted_time', 'verified_time'])

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.__blockwidget)
        mainLayout.addStretch(0)
        mainLayout.addWidget(self.__transactionWidget)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        self.__blockwidget.itemClicked.connect(self.blockClicked)

    def populate(self):
        data = database.get_blocks()
        self.__blockwidget.populate(data)

    def refresh(self):
        self.populate()
        self.__transactionWidget.populate([])

    def blockClicked(self, item):
        block = self.__blockwidget.item(item.row(), 0).text()
        transactions = database.get_transactions(block)
        self.__transactionWidget.populate(transactions)

