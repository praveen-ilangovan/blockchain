import os
import sqlite3
from contextlib import contextmanager
try:
    import simplejson as json
except ImportError:
    import json

# Local imports
from . import utils

"""
Module to access database that has the user and blockchain
information.

Module provides access to add, retrieve and delete user information.
It also provides access to add and retrieve transactions.

The database must be accessed only using the "open_database",
a context manager, defined in this module.
"""

DB_NAME                     = "blockchain.db"
DB_PATH                     = os.path.join(utils.get_resources_dir(),
                                           DB_NAME)

TABLE_WALLETS              	= "WALLETS"
COL_WALLETS_NAME           	= "NAME"
COL_WALLETS_PUB_KEY        	= "PUBLIC_KEY"
COL_WALLETS_PVT_KEY        	= "PRIVATE_KEY"

# Blockchain
    # block, num_of_transactions, total_amount, block_added_time, hash
TABLE_BLOCKCHAIN            = "BLOCKCHAIN"
COL_BLOCKCHAIN_BLOCKID      = 'BLOCK_ID'
COL_BLOCKCHAIN_BLOCK        = "BLOCK"
COL_BLOCKCHAIN_TRANS_COUNT  = "TRANS_COUNT"
COL_BLOCKCHAIN_AMOUNT       = "AMOUNT"
COL_BLOCKCHAIN_TIME         = "TIMESTAMP"
COL_BLOCKCHAIN_BLOCK_HASH   = "BLOCK_HASH"

# Transactions
    # block, sender, receiver, amount, submitted_time, verified_time
TABLE_TRANSACTIONS          = "TRANSACTIONS"
COL_TRANSACTION_BLOCK       = "BLOCK"
COL_TRANSACTION_SENDER      = "SENDER"
COL_TRANSACTION_RECEIVER    = "RECEIVER"
COL_TRANSACTION_AMOUNT      = "AMOUNT"
COL_TRANSACTION_SUB_TIME    = "SUBMITTED_TIME"
COL_TRANSACTION_VER_TIME    = "VERIFIED_TIME"

class BlockChainDB(object):
    """A class to access and retrieve information from the database.
    Should be accessed only using the open_database context manager.

    Args:
        dbcursor (sqlite3.cursor) : Cursor object of an sqlite database.
    """
    def __init__(self, dbcursor):
        self.__dbcursor = dbcursor

        # Create all the tables
        self.__create_wallets_table()
        self.__create_transactions_table()
        self.__create_blockchain_table()

    @property
    def dbcursor(self):
        """Cursor object of the connected database.

        Returns:
            sqlite3.cursor: Cursor object of the connected database.
        """
        return self.__dbcursor

    ##########################################################################
    #
    # WALLETS TABLE
    #
    ##########################################################################
    def add_wallet(self, name, pubkey, pvtkey):
        """Adds a new wallet to the database.

        Args:
            name  (str): Identifier. Must be unique.
            pubkey(bytes): RSA public key in bytes format
            pvtkey(bytes): RSA private key in bytes format
        """
        cmd = """INSERT INTO %s(%s, %s, %s) 
                    VALUES(?,?,?);""" %(TABLE_WALLETS,
                                        COL_WALLETS_NAME,
                                        COL_WALLETS_PUB_KEY,
                                        COL_WALLETS_PVT_KEY)
        self.__dbcursor.execute(cmd, (name, pubkey, pvtkey))

    def get_wallet(self, name):
        """Gets the user information from the database.

        Args:
            name  (str): Identifier. Must be unique.

        Returns:
            :obj:`tuple` of :obj:`str`, :obj:`bytes`, :obj:`bytes`
                str: Name of the user
                bytes: RSA public key in bytes format
                bytes: RSA private key in bytes format
        """
        cmd = """ SELECT %s, %s, %s FROM %s 
                    WHERE %s = '%s'; """ %(COL_WALLETS_NAME,
                                           COL_WALLETS_PUB_KEY,
                                           COL_WALLETS_PVT_KEY,
                                           TABLE_WALLETS,
                                           COL_WALLETS_NAME, name)
        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchone()

    def get_users(self):
        """Returns the names of all the wallets in the database.

        Returns:
            :obj:`list` of :obj:`str`
        """
        cmd = """ SELECT %s FROM %s; """ %(COL_WALLETS_NAME,
                                           TABLE_WALLETS)
        self.__dbcursor.execute(cmd)
        return [row[0] for row in self.__dbcursor.fetchall()]

    def remove_wallet(self, name):
        """Removes a wallet from the database.

        Args:
            name  (str): Identifier. Must be unique.
        """
        cmd = """ DELETE FROM %s WHERE %s = '%s' """ %(TABLE_WALLETS,
                                                       COL_WALLETS_NAME,
                                                       name)
        self.__dbcursor.execute(cmd)

    ##########################################################################
    #
    # TRANSACTIONS
    #
    ##########################################################################
    def add_transaction(self, block, transaction):
        """ Adds a new transaction to the database

        Args:
            block  (str): Name of the block the transaction is part of
            transaction (transaction.VerifiedTransaction) : Transaction
        """
        cmd = """INSERT INTO %s(%s, %s, %s, %s, %s, %s)
                    VALUES(?,?,?,?,?,?);""" %(TABLE_TRANSACTIONS,
                                   COL_TRANSACTION_BLOCK,
                                   COL_TRANSACTION_SENDER,
                                   COL_TRANSACTION_RECEIVER,
                                   COL_TRANSACTION_AMOUNT,
                                   COL_TRANSACTION_SUB_TIME,
                                   COL_TRANSACTION_VER_TIME)
        self.__dbcursor.execute(cmd, (block, transaction.sender,
                                      transaction.receiver,
                                      transaction.amount,
                                      transaction.submitted_time,
                                      transaction.verified_time))

    ##########################################################################
    #
    # BLOCKCHAIN
    #
    ##########################################################################
    def add_block(self, block_name, transactions, timestamp, hash_value):
        """ Adds a new block and its transactions to the database

        Args:
            block_name str: Name of the block
            transactions :obj:`list` of transaction.VerifiedTransactions
            timestamp str: Time this block will be added to the blockchain
            hash_value str: Hash
        """

        transacted_amount = 0
        for transaction in transactions:
            transacted_amount += transaction.amount
            self.add_transaction(block_name, transaction)

        cmd = """INSERT INTO %s(%s, %s, %s, %s, %s)
                    VALUES(?,?,?,?,?);""" %(TABLE_BLOCKCHAIN,
                                   COL_BLOCKCHAIN_BLOCK,
                                   COL_BLOCKCHAIN_TRANS_COUNT,
                                   COL_BLOCKCHAIN_AMOUNT,
                                   COL_BLOCKCHAIN_TIME,
                                   COL_BLOCKCHAIN_BLOCK_HASH)
        self.__dbcursor.execute(cmd, (block_name, len(transactions),
                                      transacted_amount, timestamp,
                                      hash_value))

    def get_block(self, block_name):
        """ Returns the block

        Args:
            block_name str: Name of the block

        Returns:
            tuple
        """
        cmd = """  SELECT * FROM %s WHERE %s = '%s'; """ %(
                TABLE_BLOCKCHAIN, COL_BLOCKCHAIN_BLOCK, block_name)

        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchone()

    def get_blocks(self):
        """ Returns all the blocks in the blockchain

        Returns:
            list of tuple
        """
        cmd = """  SELECT * FROM %s; """ %(TABLE_BLOCKCHAIN)

        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchall()

    def get_transactions(self, block_name):
        """ Returns all the transactions that are part of a block

        Args:
            block_name str: Name of the block

        Returns:
            list of tuple
        """
        cmd = """  SELECT * FROM %s WHERE %s = '%s'; """ %(
                TABLE_TRANSACTIONS, COL_TRANSACTION_BLOCK, block_name)

        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchall()

    def get_last_block(self):
        """ Returns the recently added block

        Args:
            block_name str: Name of the block

        Returns:
            tuple
        """
        cmd = """  SELECT * FROM %s WHERE %s = (SELECT MAX(%s) FROM %s); """ %(
                TABLE_BLOCKCHAIN, COL_BLOCKCHAIN_BLOCKID, COL_BLOCKCHAIN_BLOCKID,
                TABLE_BLOCKCHAIN)

        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchone()

    def get_last_block_hash(self):
        """ Returns the hash of the recently added block

        Args:
            block_name str: Name of the block

        Returns:
            tuple
        """
        cmd = """  SELECT %s FROM %s WHERE %s = (SELECT MAX(%s) FROM %s); """ %(
                COL_BLOCKCHAIN_BLOCK_HASH, TABLE_BLOCKCHAIN, COL_BLOCKCHAIN_BLOCKID,
                COL_BLOCKCHAIN_BLOCKID, TABLE_BLOCKCHAIN)

        self.__dbcursor.execute(cmd)
        return self.__dbcursor.fetchone()

    ##########################################################################
    #
    # CREATE TABLES
    #
    ##########################################################################
    def __create_wallets_table(self):
        """Create the wallets table if it doesn't exist
        """
        cmd = """ CREATE TABLE IF NOT EXISTS %s (
                    %s text PRIMARY KEY,
                    %s blob,
                    %s blob);""" %(TABLE_WALLETS,
                                   COL_WALLETS_NAME,
                                   COL_WALLETS_PUB_KEY,
                                   COL_WALLETS_PVT_KEY)
        self.__dbcursor.execute(cmd)

    def __create_transactions_table(self):
        """ Create a table to store all the verified transactions
        that has been added to the blockchain

        # Transactions
            # block, sender, receiver, amount, submitted_time, verified_time
        """
        cmd = """ CREATE TABLE IF NOT EXISTS %s (
                    %s text,
                    %s text,
                    %s text,
                    %s real,
                    %s text,
                    %s text);""" %(TABLE_TRANSACTIONS,
                                   COL_TRANSACTION_BLOCK,
                                   COL_TRANSACTION_SENDER,
                                   COL_TRANSACTION_RECEIVER,
                                   COL_TRANSACTION_AMOUNT,
                                   COL_TRANSACTION_SUB_TIME,
                                   COL_TRANSACTION_VER_TIME)
        self.__dbcursor.execute(cmd)

    def __create_blockchain_table(self):
        """Create the blockchain table

        # Blockchain
            # block, num_of_transactions, total_amount, block_added_time, hash
        """
        cmd = """ CREATE TABLE IF NOT EXISTS %s (
                    %s integer PRIMARY KEY AUTOINCREMENT,
                    %s text,
                    %s integer,
                    %s real,
                    %s text,
                    %s text);""" %(TABLE_BLOCKCHAIN,
                                   COL_BLOCKCHAIN_BLOCKID,
                                   COL_BLOCKCHAIN_BLOCK,
                                   COL_BLOCKCHAIN_TRANS_COUNT,
                                   COL_BLOCKCHAIN_AMOUNT,
                                   COL_BLOCKCHAIN_TIME,
                                   COL_BLOCKCHAIN_BLOCK_HASH)
        self.__dbcursor.execute(cmd)

@contextmanager
def open_database(dbpath=DB_PATH):
    """Establishes a connection to the database and gives
    access to add, remove or retrieve information from it.
    On exit, the connection is closed properly.

    Args:
        dbpath (str, optional): sqlite database file path.
            Defaults to ./accounts.db.
    """

    # __enter__ (Establish the connection)
    db = sqlite3.connect(dbpath)
    cursor = db.cursor()

    yield BlockChainDB(cursor)

    # __exit__ (Commit and close the connection)
    db.commit()
    db.close()

##############################################################################
#
# HELPER FUNCTIONS
#
##############################################################################
def add_wallet(owner, public_key, private_key):
    with open_database() as db:
        db.add_wallet(owner, public_key, private_key)

def get_wallet(owner):
    result = []
    with open_database() as db:
        result = db.get_wallet(owner)
    return result

def get_wallet_holders():
    users = []
    with open_database() as db:
        users = db.get_users()
    return users

def is_unique_name(name):
    return name not in get_wallet_holders()

def add_block(block_name, transactions):
    with open_database() as db:
        timestamp = utils.get_timestamp()

        hash_dict = {}
        hash_dict['name'] = block_name
        hash_dict['transactions'] = [t.to_json() for t in transactions]
        hash_dict['timestamp'] = timestamp

        hash_string = json.dumps(hash_dict, sort_keys=True).encode()
        hash_value = utils.hexdigest(hash_string)

        db.add_block(block_name, transactions, timestamp, hash_value)

def get_block(block_name):
    result = []
    with open_database() as db:
        result = db.get_block(block_name)

    if result:
        from . import block
        return block.Block(*result[1:])
    return result

def get_blocks():
    result = []
    with open_database() as db:
        result = db.get_blocks()

    from . import block
    return [block.Block(*r[1:]) for r in result]

def get_transactions(block_name):
    result = []
    with open_database() as db:
        result = db.get_transactions(block_name)

    from . import transaction
    return [transaction.TransactionBlock(*r) for r in result]

def get_last_block():
    result = []
    with open_database() as db:
        result = db.get_last_block()
    if result:
        from . import block
        return block.Block(*result[1:])
    return result

def get_last_block_hash():
    result = []
    with open_database() as db:
        result = db.get_last_block_hash()
    return result
