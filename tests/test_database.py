import pytest
import os

# Local imports
from ..src.database import open_database
from ..src.database import TABLE_WALLETS
from ..src import utils

TEST_DB_NAME                     = "test_blockchain.db"
TEST_DB_PATH                     = os.path.join(utils.get_resources_dir(),
                                           TEST_DB_NAME)
# Clear the file from the disk
try:
    os.remove(TEST_DB_PATH)
    print "Deleted the old test db file. A new one will be created for testing."
except OSError:
    pass

def test_db_file_exists():
    """Check if the test db file exists in the disk
    """
    with open_database(TEST_DB_PATH) as db:
        pass
    assert os.path.exists(TEST_DB_PATH)

##############################################################################
#
# WALLETS TABLE CHECK
#
##############################################################################
def test_wallets_table_exists():
    with open_database(TEST_DB_PATH) as db:
        cmd = "SELECT name FROM sqlite_master WHERE type='table';"
        db.dbcursor.execute(cmd)
        assert db.dbcursor.fetchall() == [(TABLE_WALLETS,)]

def test_add_wallets():
    sample_users = ('Praveen', 'Mrinu', 'Ishu')
    with open_database(TEST_DB_PATH) as db:
        for user in sample_users:
            db.add_wallet(user, b"This is the public key of %s" %(user),
                b"This is the private key of %s" %(user))
        assert set(db.get_users()) == set(sample_users)

def test_unique_wallet_user_name():
    """This check should throw an integrity error as
    Praveen isn't a unique name.
    """
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        with open_database(TEST_DB_PATH) as db:
            db.add_wallet('Praveen', b"pub", b"pvt")

def test_get_wallet():
    with open_database(TEST_DB_PATH) as db:
        wallet = db.get_wallet('Ishu')
        assert wallet[0] == 'Ishu'

def test_get_invalid_wallet():
    with open_database(TEST_DB_PATH) as db:
        wallet = db.get_wallet('Ishuu')
        assert wallet == None

def test_remove_wallet():
    with open_database(TEST_DB_PATH) as db:
        db.remove_wallet('Praveen')
        assert set(db.get_users()) == set(['Ishu', 'Mrinu'])
