import os
import unittest

from database import Database

class TestDatabaseMethods(unittest.TestCase):
    """Test all the methods that get data from the database"""
    def setUp(self):
        self.database_inst = Database("Test.db")

        #Create tables
        self.database_inst.create_table("Test1", ("Test1", "Test2", "Test3"))
        self.database_inst.create_table("Test2", ("'Test1' TEXT", "'Test2' INTEGER", "'Test3' OTHER"))
        self.database_inst.create_table("Test3", ("'Test1' INTEGER", "'Test2' TEXT", "'Test3' TEXT"))

        #Add data to the tables
        """The get_columns test will fail if add_row_to_table function fails"""
        self.database_inst.add_row_to_table("Test1", (("Test1", "Item1"), ("Test2", "Item2")))
        self.database_inst.add_row_to_table("Test2", (("Test1", "Item1"), ("Test2", "Item2")))
        self.database_inst.add_row_to_table("Test3", (("Test1", "Item1"), ("Test2", "Item2"), ("Test3", "Item3")))
        self.database_inst.add_row_to_table("Test3", (("Test2", "Item1"), ("Test1", "Item2"), ("Test3", "Item3")))

    def test_mirror_delete_table(self):
        new_name1 = self.database_inst.mirror_delete_table("Test1")
        new_name2 = self.database_inst.mirror_delete_table("Test2")
        new_name3 = self.database_inst.mirror_delete_table("Test3")

        self.assertEqual(self.database_inst.get_all_table_data(new_name1), [("Item1", "Item2", 'None')])
        self.assertEqual(self.database_inst.get_all_table_data(new_name2), [("Item1", "Item2", 'None')])
        self.assertEqual(self.database_inst.get_all_table_data(new_name3), [("Item1", "Item2", "Item3"), ("Item2", "Item1", "Item3")])

        with self.assertRaises(Exception):
            self.database_inst.mirror_delete_table("Test1")
        with self.assertRaises(Exception):
            self.database_inst.mirror_delete_table("Test2")
        with self.assertRaises(Exception):
            self.database_inst.mirror_delete_table("Test3")

    def test_update_row_to_table(self):
        pass #Will be added later when the funtion is redone #Will be added later when the funtion is redone

    def test_delete_table_data(self):
        pass #Will be added later when the funtion is redone #Will be added later when the funtion is redone

    def test_get_columns(self):
        """Test getting columns"""
        self.assertEqual(self.database_inst.get_table_columns("Test1"), 
                         (("Test1", ''), ("Test2", ''), ("Test3", '')))
        self.assertEqual(self.database_inst.get_table_columns("Test2"), 
                         (("Test1", 'TEXT'), ("Test2", 'INTEGER'), ("Test3", 'OTHER')))
        self.assertEqual(self.database_inst.get_table_columns("Test3"), 
                         (("Test1", 'INTEGER'), ("Test2", 'TEXT'), ("Test3", 'TEXT')))
        
    def test_get_all_table_data(self):
        """Test getting all the table data"""    
        self.assertEqual(self.database_inst.get_all_table_data("Test1"), [("Item1", "Item2", None)])
        self.assertEqual(self.database_inst.get_all_table_data("Test2"), [("Item1", "Item2", None)])
        self.assertEqual(self.database_inst.get_all_table_data("Test3"), [("Item1", "Item2", "Item3"), ("Item2", "Item1", "Item3")])

    def tearDown(self):
        self.database_inst.close_connection()
        os.remove("./Test.db")

if (__name__ == "__main__"):
    #Making sure the test database is removed
    try:
        os.remove("./Test.db")
    except:
        pass

    unittest.main()

