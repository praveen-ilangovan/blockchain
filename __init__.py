# USAGE : python -m blockchain

"""
A simple implementation of blockchain technology in python
using its cryptography module.

cryptography ==> https://cryptography.io/en/latest/

Example:
	import blockchain

	# Create a few wallets
	user1 = blockchain.generate_wallet("User1", "User1Password")
	user2 = blockchain.generate_wallet("User2", "User2Password")
	user3 = blockchain.generate_wallet("User3", "User3Password")

	# Make a few transactions
	blockchain.submit_transaction('User1', 'User2', 2.0, "User1Password")
	blockchain.submit_transaction('User2', 'User3', 1.5, "User2Password")
	blockchain.submit_transaction('User3', 'User1', 2.55, "User3Password")
	blockchain.submit_transaction('User2', 'User1', 2.01, "User2Password")

	# Add them to the blockchain
	blockchain.mine()
"""

##############################################################################
#
# Main functions that will be used mostly in making a transaction and
# adding it to the blockchain.
#
##############################################################################

# Generate a wallet
#	==> generate_wallet(name str, password str)
from .src.wallet import generate_wallet
# Submit a transaction
#	==> submit_transaction(sender str, receiver str, amount float, password str)
from .src.transaction import submit_transaction
# Kick start mining and add the transactions to the blockchain
#	==> mine()
from .src.mining import mine
