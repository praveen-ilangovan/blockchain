from uuid import uuid4

from . import transaction
from . import database
from . import utils
from .block import Block
from ..logger import LOG

MINING_DIFFICULTY = 2
MINING_DIGIT = "0"
MINING_PREFIX = MINING_DIGIT*MINING_DIFFICULTY

"""
Mining is the process by which the transactions are added
to the blockchain as a block. These blocks are immutable.
Transactions once added to the blockchain remains there forever.
They cannot be edited.

The program has to solve a cryptographic puzzle before adding
a block to the blockchain. This step is called proof of work.
"""

class Mining(object):
    def __init__(self):
        self.__transactions = []

    def proof_of_work(self):
        """ Look for the nonce value that generates
        a hash that satisifes a specific condition.

        In our case, the first "MINING_DIFFICULTY" number
        of digits has to be the "MINING_DIGIT"
        (i.e) the hash should begin as "00"

        Returns:
            the nonce number
        """
        # get the last block hash
        last_block_hash = database.get_last_block_hash()
        # if blockchain is empty
        if last_block_hash == None:
            last_block_hash = "00"

        # proof of work
        message = str(self.__transactions) + str(last_block_hash)

        nonce = 0
        while self._found_match(message, nonce) is False:
            nonce += 1
        return nonce

    def _found_match(self, message, nonce):
        guess = (str(message)+str(nonce)).encode()
        guess_hash = utils.hexdigest(guess)
        return guess_hash[:MINING_DIFFICULTY] == MINING_PREFIX

    def add_to_blockchain(self):
        """ Add a new block to the blockchain
        """
        name = str(uuid4()).replace('-', '')
        database.add_block(name, self.__transactions)
        transaction.clear_transactions()

    def mine(self):
        """ Mines a new block and adds it to the blockchain.

        """
        # get verified transactions
        self.__transactions = transaction.verify_pending_transactions()
        if not self.__transactions:
            LOG.warning("No transactions found to add to the blockchain.")
            return

        nonce = self.proof_of_work()

        # add to blockchain
        self.add_to_blockchain()

##############################################################################
#
# HELPERS
#
##############################################################################

def mine():
    mining = Mining()
    mining.mine()
