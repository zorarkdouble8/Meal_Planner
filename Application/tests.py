import os
import unittest
import sqlite3

import database

class Database_Tests(unittest.TestCase):
    def setUp(self):
        database.initialize("Test.db")

    def test_create_table(self):
        """Test basic creation functionality"""
        database.create_table("Testing", ("Test1", "Test2", "Test3"))

        columns = database.get_table_columns("Testing")
        answer_columns = (("Test1", ''), ("Test2", ''), ("Test3", ''))
        self.assertEqual(columns, answer_columns)

    def tearDown(self):
        database.close_connection()
        os.remove(".\Test.db")

if (__name__ == "__main__"):
    unittest.main()

