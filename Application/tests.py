import os
import unittest
import shutil

from database import Database
from updater import Updater

class TestDatabaseMethods(unittest.TestCase):
    """Test all the methods that get data from the database"""
    def setUp(self):
        self.database = Database("Test.db")

        #Create tables
        self.database.create_table("Test1", ("Test1", "Test2", "Test3"))
        self.database.create_table("Test2", ("'Test1' TEXT", "'Test2' INTEGER", "'Test3' OTHER"))
        self.database.create_table("Test3", ("'Test1' INTEGER", "'Test2' TEXT", "'Test3' TEXT"))

        #Add data to the tables
        """The get_columns test will fail if add_row_to_table function fails"""
        self.database.add_row_to_table("Test1", (("Test1", "Item1"), ("Test2", "Item2")))
        self.database.add_row_to_table("Test2", (("Test1", "Item1"), ("Test2", "Item2")))
        self.database.add_row_to_table("Test3", (("Test1", "Item1"), ("Test2", "Item2"), ("Test3", "Item3")))
        self.database.add_row_to_table("Test3", (("Test2", "Item1"), ("Test1", "Item2"), ("Test3", "Item3")))

    def test_mirror_delete_table(self):
        new_name1 = self.database.mirror_delete_table("Test1")
        new_name2 = self.database.mirror_delete_table("Test2")
        new_name3 = self.database.mirror_delete_table("Test3")

        self.assertEqual(self.database.get_all_table_data(new_name1), [("Item1", "Item2", 'None')])
        self.assertEqual(self.database.get_all_table_data(new_name2), [("Item1", "Item2", 'None')])
        self.assertEqual(self.database.get_all_table_data(new_name3), [("Item1", "Item2", "Item3"), ("Item2", "Item1", "Item3")])

        with self.assertRaises(Exception):
            self.database.mirror_delete_table("Test1")
        with self.assertRaises(Exception):
            self.database.mirror_delete_table("Test2")
        with self.assertRaises(Exception):
            self.database.mirror_delete_table("Test3")

    def test_update_row_to_table(self):
        pass #Will be added later when the funtion is redone #Will be added later when the funtion is redone

    def test_delete_table_data(self):
        pass #Will be added later when the funtion is redone #Will be added later when the funtion is redone

    def test_get_columns(self):
        """Test getting columns"""
        self.assertEqual(self.database.get_table_columns("Test1")["Names"], 
                         ("Test1", "Test2", "Test3"))
        self.assertEqual(self.database.get_table_columns("Test2")["Types"], 
                         ('TEXT', 'INTEGER', 'OTHER'))
        self.assertEqual(self.database.get_table_columns("Test3"), 
                         {"Names": ("Test1", "Test2", "Test3"),"Types": ("INTEGER", 'TEXT', 'TEXT')})
        
    def test_get_all_table_data(self):
        """Test getting all the table data"""    
        self.assertEqual(self.database.get_all_table_data("Test1"), [("Item1", "Item2", None)])
        self.assertEqual(self.database.get_all_table_data("Test2"), [("Item1", "Item2", None)])
        self.assertEqual(self.database.get_all_table_data("Test3"), [("Item1", "Item2", "Item3"), ("Item2", "Item1", "Item3")])

    def tearDown(self):
        self.database.close_connection()
        os.remove("./Test.db")

class TestUpdater(unittest.TestCase):
    def setUp(self):
        self.database = Database("Test.db")

        shutil.copyfile("Application/Definitions/Test_definitions/test1.json", "Application/Definitions/Test_definitions/test1Copy.json")
        shutil.copyfile("Application/Definitions/Test_definitions/test2.json", "Application/Definitions/Test_definitions/test2Copy.json")

        self.updater1 =  Updater(self.database, file="Application/Definitions/Test_definitions/test1.json")
        self.updater2 =  Updater(self.database, file="Application/Definitions/Test_definitions/test2.json")


    def test_check_update(self):
        self.assertTrue(self.updater1.check_update())
        self.assertFalse(self.updater2.check_update())

    def test_update(self):
        self.updater1.update() 

    def tearDown(self):
        self.database.close_connection()
        os.remove("./Test.db")

        shutil.copyfile("Application/Definitions/Test_definitions/test1Copy.json", "Application/Definitions/Test_definitions/test1.json")
        os.remove("Application/Definitions/Test_definitions/test1Copy.json")

        shutil.copyfile("Application/Definitions/Test_definitions/test2Copy.json", "Application/Definitions/Test_definitions/test2.json")
        os.remove("Application/Definitions/Test_definitions/test2Copy.json")

if (__name__ == "__main__"):
    #Making sure the test database is removed
    try:
        os.remove("./Test.db")
    except:
        pass
     
    unittest.main()

