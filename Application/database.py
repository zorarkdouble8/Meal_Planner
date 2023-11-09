import sqlite3
import json

class Database():
    def __init__(self, database_file="Food.db"):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def save_database(self):
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def check_fix_database(self):
        """Checks the database and fixs any problems that occur"""
        try:
            with open("Application\Definitions\database_definition.json", "r") as file:
                data_dict = json.load(file)

            self.check_database_definition(data_dict)
        except Exception as error:
            raise Exception(error)

    def check_database_definition(self, data_dict):
        """checks if the database is equal to the definition
        
        Returns: String (any error that occured)
        """
        try:
            table_list = self.cursor.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
            table_list = [table[0] for table in table_list]

            for table in data_dict["Tables"]:
                if (table not in table_list):
                    self.create_table(table, column_names=data_dict["Tables"][table]["Columns"], options=data_dict["Tables"][table]["Options"])
                else:
                    #Check if the table column's are consistant with the definitions
                    table_columns = self.get_table_columns(table)
                    def_columns = tuple(data_dict["Tables"][table]["Columns"])

                    if (len(def_columns) != len(table_columns)):
                        raise Exception("Tables lengths are not consistant!")
                    else:
                        #Check if the names are the same
                        for x in range(0, len(def_columns)):
                            if (f"'{table_columns[x][0]}' {table_columns[x][1]}" != def_columns[x]):
                                raise Exception(f"Columns don't match! '{table_columns[x][0]}' {table_columns[x][1]} != {def_columns[x]}")
                            
            self.connection.commit()
        except Exception as error:
            raise Exception(error)

    def create_table(self, table_name, column_names, options=None):
        """Adds a table to the database

        Arguments: table_name (string)
                column_names (tuple or list)
                options (string) used for adding contraints
        """
        try:
            if (options == None):
                self.cursor.execute(f"CREATE TABLE {table_name}({','.join(column_names)})")
            else: 
                self.cursor.execute(f"CREATE TABLE {table_name}({','.join(column_names)}, {','.join(options)})")
        except Exception as error:
            raise Exception(error)

    def get_table_columns(self, table_name):
        """Returns the columns from a table
        
        Returns 2D Tuple (('Name', 'Type'))
        """
        try:
            column_names = self.cursor.execute(f"SELECT name, type FROM PRAGMA_TABLE_INFO('{table_name}')").fetchall()

            name_list = [name for name in column_names]
            return tuple(name_list)
        except Exception as error:
            raise Exception(error)

    def mirror_delete_table(self, table_name): 
        """creates a mirror of a table and then deletes it. This returns the new_table_name or False if unsuccessful
        
            Arguements: table_name (string)
        """

        try:
            column_names = [col_def[0] for col_def in self.get_table_columns(table_name)]

            table_data = self.get_all_table_data(table_name)
            new_table_name = table_name + "_Mirror"

            self.create_table(new_table_name, column_names)

            for row in table_data:
                self.cursor.execute(f"INSERT INTO {new_table_name} {tuple(column_names)} VALUES {tuple(str(element) for element in row)}")
            
            self.cursor.execute(f"DROP TABLE {table_name}")

            return new_table_name
        except Exception as error:
            raise Exception(error)

    def add_row_to_table(self, table_name, data):
        """Adds a row of data to a table in the database
        
        Arguments: table_name (string)
                    data (tuple or list in the form: (column_name, data))          
        """
        try:
            columns = []
            values = []

            for column, value in data:
                columns.append(column.title())
                values.append(value)

            self.cursor.execute(f"INSERT INTO {table_name} {tuple(columns)} VALUES {tuple(values)}")
        except Exception as error:
            raise Exception(error)

    def update_row_to_table(self, table_name, id, data):
        """Adds a row of data to a table in the database
        
        Arguments: table_name (string)
                    id (int (the unique identifier of the row))
                    data (tuple or list in the form: (column, data))          
        """
        try:
            columns = []
            values = []

            for column, value in data:
                columns.append(column.title())
                values.append(value)

            self.cursor.execute(f"UPDATE {table_name} SET {tuple(columns)} = {tuple(values)} WHERE ID={id}")
        except Exception as e:
            raise Exception(e)

    def delete_table_data(self, data_index, table_name):
        """Deletes a row of data using a unique data index
        
        Parameters: data_index (int or string (the unique ID))
                    table_name (string)"""
        
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE ID={data_index}")
        except Exception as error:
            raise Exception(error)
        
    def get_all_table_data(self, table_name): #Can cause error
        """Gets all the table data using a table name
        
        Arguements: table_name (string, the name of the table)
        Returns: array tuple (In the form: [(column1 row1 data, column2 row1 data), 
                                            (column1 row2 data, column2 row2 data)])
        """
        try:
            return self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        except Exception as error:
            raise Exception(error)