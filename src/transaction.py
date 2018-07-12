import os

try:
    import simplejson as json
except ImportError:
    import json

# Local imports
from .wallet import Wallet
from . import utils
from ..logger import LOG

"""
Wallet holder sends dummycoins to another wallet holder
by making a transaction. This stores the information of the
name of the sender, receiver and amount of dummycoin to be
transferred.

The sender's private key is used to sign the transaction.
Transactions are stored in a file on disk until they are
verified by the miner and added to a block. Miner uses the
sender's public key to verify it.
"""

# File on disk to store the transactions that have not been
# verified by a miner yet.
PENDING_TRANSACTIONS_FILE = os.path.join(utils.get_resources_dir(),
    "pending_transactions.json")

class JsonSerializable(object):
    def to_json(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return self.to_json()

class BaseTransaction(JsonSerializable):
    """ A base class to hold the basic information of a transaction.

    Args:
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
    """
    def __init__(self, sender, receiver, amount):
        self.__sender = sender
        self.__receiver = receiver
        self.__amount = amount

    @property
    def sender(self):
        return self.__sender

    @property
    def receiver(self):
        return self.__receiver

    @property
    def amount(self):
        return self.__amount

    def __str__(self):
        return "%s('%s', '%s', '%s')" %(self.__class__.__name__, self.__sender,
                                        self.__receiver, self.__amount)

class PendingTransaction(BaseTransaction):
    """ A transaction is a pending transaction until it's sender's
    sign is verified by a miner and added to the blockchain.

    When a transaction is made, its sender has to sign it using his
    wallet's private key.

    Args:
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
    """
    def __init__(self, sender, receiver, amount):
        super(PendingTransaction, self).__init__(sender, receiver, amount)

    @property
    def message(self):
        return "{} sends {} dummycoins to {}".format(self.sender,
            self.amount, self.receiver)

    def get_sender_wallet(self):
        sender_wallet = Wallet.load_from_database(self.sender)
        if not sender_wallet:
            return None
        return sender_wallet

    def sign(self, password):
        """ The transaction is signed using sender's private key.
        Password is required to access the private key that is
        stored in the database.

        Args:
            password str: Password of the sender's wallet.

        Returns:
            str : signature
        """
        sender_wallet = self.get_sender_wallet()
        if not sender_wallet:
            return None

        return sender_wallet.sign(self.message, password)

    def verify(self, signature):
        """ The transaction is verified using sender's public key.

        Args:
            signature str: Signature generated using sender's private key.

        Returns:
            bool : True if verification passed.
        """
        sender_wallet = self.get_sender_wallet()
        if not sender_wallet:
            return None

        return sender_wallet.verify(self.message, signature)

class VerifiedTransaction(BaseTransaction):
    """ VerirfiedTransaction is a transaction that has been verified
    and ready to be added to the blockchain.

    Args:
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
        submitted_time str: Time when the transaction was signed and submitted
                by the sender.
        verified_time str: Time when the transaction was verified and added to
                the blockchain.
    """
    def __init__(self, sender, receiver, amount, submitted_time,
                 verified_time):
        super(VerifiedTransaction, self).__init__(sender, receiver, amount)
        self.__submitted_time = submitted_time
        self.__verified_time = verified_time

    @property
    def submitted_time(self):
        return self.__submitted_time

    @property
    def verified_time(self):
        return self.__verified_time

class TransactionBlock(VerifiedTransaction):
    """ Transaction block is a transaction that has been verified and added
    to the blockchain.

    Args:
        block_name str: Name of the block it belongs to in the blockchain.
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
        submitted_time str: Time when the transaction was signed and submitted
                by the sender.
        verified_time str: Time when the transaction was verified and added to
                the blockchain.
    """
    @classmethod
    def load_from_database(cls, result):
        """ Create an instance of TransactionBlock using the result returned
        by the database.

        Args:
            result `obj`:`tuple` of `obj`:`str`:(block_name, sender, receiver,
                                                    amount, submitted_time,
                                                    verified_time)

        Returns:
            TransactionBlock
        """
        if len(result) != 6:
            LOG.error("Failed to create a VerifiedTransaction instance. Not enough \
                values returned by the database to unpack.")
            return None

        return cls(*result)

    def __init__(self, block_name, sender, receiver, amount,
                 submitted_time, verified_time):
        super(TransactionBlock, self).__init__(sender, receiver, amount,
                                           submitted_time, verified_time)
        self.__block_name = block_name

    @property
    def block_name(self):
        return self.__block_name

    def __getitem__(self, attr):
        if attr == 'sender':
            return self.sender
        elif attr == 'receiver':
            return self.receiver
        elif attr == 'amount':
            return self.amount
        elif attr == 'submitted_time':
            return self.submitted_time
        elif attr == 'verified_time':
            return self.verified_time
        return ''

##############################################################################
#
# Functions to submit and verify transactions
#
##############################################################################
def submit_transaction(sender, receiver, amount, password):
    """ A new transaction is added to the list of pending transactions
    which would then be added to the block. The transaction is signed using
    sender's private key.

    Args:
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
        password str: Password of the sender's wallet.
    """
    transaction = PendingTransaction(sender, receiver, amount)
    signature = transaction.sign(password)
    if not signature:
        return False

    transactions = get_pending_transactions()
    transactions.append( {'sender' : sender,
                          'receiver' : receiver,
                          'amount' : amount,
                          'signature' : signature,
                          'submitted_time' : utils.get_timestamp()} )

    with open(PENDING_TRANSACTIONS_FILE, "w+") as f:
        json.dump(transactions, f, sort_keys=True, ensure_ascii=False, indent=4)

    LOG.info("Transaction is successful. Soon this will be verified and \
        added to a block.")
    return True

def verify_transaction(transaction):
    """ The transaction is verified using sender's public key to make sure
    that it was the sender who submitted this transaction.

    Args:
        sender str: Name of the sender. Sender must have a wallet.
        receiver str: Name of the receiver. Receiver must have a wallet.
        amount float: Amount to be transferred.
        signature str: Signature generated using sender's private key.
    """
    pending = PendingTransaction(transaction['sender'], transaction['receiver'],
                                     transaction['amount'])
    return pending.verify(transaction['signature'])

def verify_pending_transactions():
    return [ VerifiedTransaction(t['sender'], t['receiver'], t['amount'],
                                 t['submitted_time'], utils.get_timestamp())
                for t in get_pending_transactions() if verify_transaction(t)]

##############################################################################
#
# Functions to access the file on disk.
#
##############################################################################
def get_pending_transactions():
    """ Get all the pending transactions that are yet to be verified
    and added to a block

    Returns:
        :obj:`list` of :obj:`dict`

    Sample return list:
        [ {'semder'     : str,
           'receiver'   : str,
           'amount'     : float,
           'signature'  : str,
           'submitted_time' : str}
        ]
    """
    data = []

    if not os.path.exists(PENDING_TRANSACTIONS_FILE):
        return data

    with open(PENDING_TRANSACTIONS_FILE, "r") as f:
        data = json.load(f)
    return data

def clear_transactions():
    """ Clears all the pending transactions.
    """
    with open(PENDING_TRANSACTIONS_FILE, "w+") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    LOG.debug("All transactions have been cleared.")
