import os

try:
	import simplejson as json
except ImportError:
	import json

# Local imports
from .wallet import Wallet
from . import utils

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

class Transaction(object):
	""" A class that holds the information of the sender,
	receiver and amount to be transferred.

	This class also provides the functionality to sign and verify
	the transaction.

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

	@property	
	def message(self):
		return "{} sends {} dummycoins to {}".format(self.__sender,
			self.__amount, self.__receiver)

	def sign_transaction(self, password):
		""" The transaction is signed using sender's private key.
		Password is required to access the private key that is
		stored in the database.

		Args:
			password str: Password of the sender's wallet.

		Returns:
			str : signature
		"""
		sender_wallet = Wallet.load_from_database(self.__sender)
		if not sender_wallet:
			return None

		return sender_wallet.sign(self.message, password)

	def verify_transaction(self, signature):
		""" The transaction is verified using sender's public key.

		Args:
			signature str: Signature generated using sender's private key.

		Returns:
			bool : True if verification passed.
		"""
		sender_wallet = Wallet.load_from_database(self.__sender)
		if not sender_wallet:
			return None

		return sender_wallet.verify(self.message, signature)

	def submit(self, password):
		""" Transaction is signed and added to the pending
		transactions file.

		Args:
			password str: Password of the sender's wallet.
		"""
		signature = self.sign_transaction(password)

		data = {'sender' : self.__sender,
				'receiver' : self.__receiver,
				'amount' : self.__amount,
				'signature' : signature,
				'submitted_time' : utils.get_timestamp()}

		add_to_pending_transactions([data])

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
	transaction = Transaction(sender, receiver, amount)
	signature = transaction.sign_transaction(password)
	if not signature:
		return False

	transactions = get_pending_transactions()
	transactions.append( {'sender' : sender,
						  'receiver' : receiver,
						  'amount' : amount,
						  'signature' : signature,
						  'submitted_time' : utils.get_timestamp()} )

	with open(PENDING_TRANSACTIONS_FILE, "w+") as f:
		json.dump(transactions, f, ensure_ascii=False, indent=4)

def verify_transaction(sender, receiver, amount, signature):
	""" The transaction is verified using sender's public key to make sure
	that it was the sender who submitted this transaction.

	Args:
		sender str: Name of the sender. Sender must have a wallet.
		receiver str: Name of the receiver. Receiver must have a wallet.
		amount float: Amount to be transferred.
		signature str: Signature generated using sender's private key.
	"""
	transaction = Transaction(sender, receiver, amount)
	return transaction.verify_transaction(signature)

def get_pending_transactions():
	""" Get all the pending transactions that are yet to be verified
	and added to a block

	Returns:
		:obj:`list` of :obj:`dict`

	Sample return list:
		[ {'semder' 	: str,
		   'receiver' 	: str,
		   'amount' 	: float,
		   'signature' 	: str,
		   'submitted_time'	: str} 
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


