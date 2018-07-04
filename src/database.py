import os
import sqlite3
from contextlib import contextmanager

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

TABLE_BLOCK_PREFIX          = "BLOCK_"
COL_BLOCK_SENDER            = "SENDER"
COL_BLOCK_RECEIVER          = "RECEIVER"
COL_BLOCK_AMOUNT            = "AMOUNT"
COL_BLOCK_TIME              = "TIMESTAMP"

TABLE_BLOCKCHAIN            = "BLOCKCHAIN"
COL_BLOCKCHAIN_BLOCK        = "BLOCK"
COL_BLOCKCHAIN_TRANS_COUNT  = "TRANS_COUNT"
COL_BLOCKCHAIN_AMOUNT       = "AMOUNT"
COL_BLOCKCHAIN_TIME         = "TIMESTAMP"

class BlockChainDB(object):
    """A class to access and retrieve information from the database.
    Should be accessed only using the open_database context manager.

    Args:
        dbcursor (sqlite3.cursor) : Cursor object of an sqlite database.
    """
    def __init__(self, dbcursor):
        self.__dbcursor = dbcursor
        self.__create_wallets_table()

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

    def __create_block_table(self, name):
        """Create a blocks table
        """
        cmd = """ CREATE TABLE %s (
                    %s text,
                    %s text,
                    %s real,
                    %s text);""" %(name,
                                   COL_BLOCK_SENDER,
                                   COL_BLOCK_RECEIVER,
                                   COL_BLOCK_AMOUNT,
                                   COL_BLOCK_TIME)
        self.__dbcursor.execute(cmd)

    def __create_blockchain_table(self):
        """Create the blockchain table
        """
        cmd = """ CREATE TABLE IF NOT EXISTS %s (
                    %s text PRIMARY KEY,
                    %s text,
                    %s real,
                    %s text);""" %(TABLE_BLOCKCHAIN,
                                   COL_BLOCKCHAIN_BLOCK,
                                   COL_BLOCKCHAIN_TRANS_COUNT,
                                   COL_BLOCKCHAIN_AMOUNT,
                                   COL_BLOCKCHAIN_TIME)
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

def is_unique_name(name):
    users = []
    with open_database() as db:
        users = db.get_users()
    return name not in users

def add_wallet(owner, public_key, private_key):
    with open_database() as db:
        db.add_wallet(owner, public_key, private_key)

def get_wallet(owner):
    result = []
    with open_database() as db:
        result = db.get_wallet(owner)
    return result