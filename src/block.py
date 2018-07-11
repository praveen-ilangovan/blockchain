
# Local imports
from . import database

"""
Blockchain is made of blocks of transactions.
Each block may have any number of transactions.
"""

class Block(object):
    def __init__(self, name, count, amount,
                 added_time='', hash_value=''):
        self.__name = name
        self.__num_of_transactions = count
        self.__transacted_amount = amount
        self.__hash = hash_value
        self.__added_time = added_time

        self.__transactions = None

    @property
    def name(self):
        return self.__name

    @property
    def transactions(self):
        if self.__transactions == None:
            self.__transactions = self.__get_transactions()
        return self.__transactions

    @property
    def num_of_transactions(self):
        return self.__num_of_transactions

    @property
    def transacted_amount(self):
        return self.__transacted_amount

    @property
    def hash(self):
        return self.__hash

    @property
    def added_time(self):
        return self.__added_time

    def __get_transactions(self):
        return database.get_transactions(self.__name)

    def __str__(self):
        return "Block(%s, %s, %s)" %(self.__name,
            self.__num_of_transactions, self.__transacted_amount)
