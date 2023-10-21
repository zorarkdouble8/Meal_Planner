import unittest
import sqlite3

import database

def initialize():
    global __connection__ 
    __connection__ = sqlite3.connect("Test.db")

    global __cursor__
    __cursor__ = __connection__.cursor()

class Database_Tests():
    def __init__(self) -> None:
        pass

    #TODO add test cases


if (__name__ == "__main__"):
    database.initialize("Test.db")
    initialize()
    unittest.main()