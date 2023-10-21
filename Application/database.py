import sqlite3
import json

def initialize(database = "Food.db"):
    global __connection__ 
    __connection__ = sqlite3.connect(database)

    global __cursor__
    __cursor__ = __connection__.cursor()

def save_database():
    __connection__.commit()

def check_fix_database(): #Checks the database and fixs any problems
    """Checks the database and fixs any problems that occur"""
    try:
        with open("Application\Definitions\database_definition.json", "r") as file:
            data_dict = json.load(file)

        check_database_definition(data_dict)
    except Exception as error:
        raise Exception(error)

def check_database_definition(data_dict): # TODO Error handling
    """checks if the database is equal to the definition
    
    Returns: String (any error that occured
    )"""
    try:
        table_list = __cursor__.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
        table_list = [table[0] for table in table_list]

        for table in data_dict["Tables"]:
            if (table not in table_list):
                create_table(table, column_names=data_dict["Tables"][table]["Columns"], options=data_dict["Tables"][table]["Options"])
            else:
                #Check if the table column's are consistant with the definitions
                table_columns = get_table_columns(table)
                def_columns = tuple(data_dict["Tables"][table]["Columns"])

                if (len(def_columns) != len(table_columns)):
                    raise Exception("Tables lengths are not consistant!")
                else:
                    #Check if the names are the same
                    for x in range(0, len(def_columns)):
                        if (f"'{table_columns[x][0]}' {table_columns[x][1]}" != def_columns[x]):
                            raise Exception(f"Columns don't match! '{table_columns[x][0]}' != {def_columns[x]}")
    except Exception as error:
        raise Exception(error)
    __connection__.commit()

def check_update():
    """Checks if there's an update available inside the definition.json
    
    Returns False (No update)
            True (update)
    """
    try:
        with open("Application\Definitions\database_definition.json", "r+") as file:
            data_dict = json.load(file)

            if ("Migration" in data_dict.keys()):
                return True
            else:
                return False
    except Exception as error:
        raise Exception(error)

def update():
    """Updates the database"""
    try:
        with open("Application\Definitions\database_definition.json", "r+") as file:
            data_dict = json.load(file)

            if (update_database(data_dict) == True):
                new_data_dic = migrate_definitions(data_dict)

                file.seek(0)
                json.dump(new_data_dic, file, indent=4)
                file.truncate()
    except Exception as error:
        return error

def migrate_definitions(data_dict): #will migrate the migration to the definition
    try:
        data_dict["Version"] = data_dict["Migration"]["Version"]
        data_dict["Tables"] = data_dict["Migration"]["Tables"]

        for table in data_dict["Tables"]:
            data_dict["Tables"][table]["Columns"] = data_dict["Migration"]["Tables"][table]["New_Columns"]
            data_dict["Tables"][table]["Options"] = data_dict["Migration"]["Tables"][table]["Options"]
            del data_dict["Tables"][table]["New_Columns"]
            del data_dict["Tables"][table]["Old_Columns"]

        del data_dict["Migration"]

        return data_dict 
    except Exception as error:
        raise Exception(error)

def update_database(data_dict):
    """Updates the database to the new definition
    
    Parameters: data_dict (dict of the data from the database definition)
    """
    try:
        table_list = __cursor__.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
        table_list = [table[0] for table in table_list]

        for table in data_dict["Migration"]["Tables"]:
            if (table_list == None):
                #Create the table
                create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                    options=data_dict["Migration"]["Tables"][table]["Options"])
            elif (table not in table_list):
                create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                    options=data_dict["Migration"]["Tables"][table]["Options"])
            else:
                #Check if the table column's are consistant with the new definition
                table_columns = get_table_columns(table)
                def_columns = data_dict["Migration"]["Tables"][table]["New_Columns"]

                if (len(def_columns) < len(table_columns)):
                    raise Exception("There are more table columns than the new definition columns, Cannot downsize")
                else:
                    #Rewrite all tables
                    mirror_table_name = mirror_delete_table(table)
                    create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                        options=data_dict["Migration"]["Tables"][table]["Options"])

                    #Place old data into new table
                    data = get_all_table_data(mirror_table_name)

                    if (len(data) != 0):
                        __cursor__.execute(f"INSERT INTO {table} {tuple(data)} VALUES {tuple(table_columns)}")

                    __cursor__.execute(f"DROP TABLE {mirror_table_name}")
            
        __connection__.commit()
    except Exception as error:
        raise Exception(error)

def create_table(table_name, column_names, options=None):
    """Adds a table to the database

    Arguments: table_name (string)
              column_names (tuple or list)
              options (string) used for adding contraints
    """
    try:
        if (options == None):
            __cursor__.execute(f"CREATE TABLE {table_name}({','.join(column_names)})")
        else: 
            __cursor__.execute(f"CREATE TABLE {table_name}({','.join(column_names)}, {','.join(options)})")
    except Exception as error:
        raise Exception(error)

def get_table_columns(table_name):
    """Returns the columns from a table
    
    Returns 2D Tuple (('Name', 'Type'))
    """
    try:
        column_names = __cursor__.execute(f"SELECT name, type FROM PRAGMA_TABLE_INFO('{table_name}')").fetchall()

        name_list = [name for name in column_names]
        return tuple(name_list)
    except Exception as error:
        raise Exception(error)

#Creates a mirror of a table and then deletes it. This returns the new_table_name or False if unsuccessful
def mirror_delete_table(table_name): #TODO Error catching
    """reates a mirror of a table and then deletes it. This returns the new_table_name or False if unsuccessful
    
        Arguements: table_name (string)
    """

    try:
        column_names = [col_def[0] for col_def in get_table_columns(table_name)]

        table_data = get_all_table_data(table_name)
        new_table_name = table_name + "_Mirror"

        create_table(new_table_name, column_names)

        for row in table_data:
            __cursor__.execute(f"INSERT INTO {new_table_name} {tuple(column_names)} VALUES {tuple(str(element) for element in row)}")
        
        __cursor__.execute(f"DROP TABLE {table_name}")

        return new_table_name
    except Exception as error:
        raise Exception(error)

def add_row_to_table(table_name, data):
    """Adds a row of data to a table in the database
    
    Arguements: table_name (string)
                data (tuple or list in the form: (column, data))          
    """
    try:
        columns = []
        values = []

        for column, value in data:
            columns.append(column.title())
            values.append(value)

        __cursor__.execute(f"INSERT INTO {table_name} {tuple(columns)} VALUES {tuple(values)}")
    except Exception as error:
        raise Exception(error)

#adds a meal to database where meal is a list or tuple of the columns in the meal table
def add_meal(meal): #TODO make this modular, make this add data into table, Error handling
    column_names = get_table_columns("Meals")

    list_meal = list(meal)
    list_column_names = list(column_names)
    
    #Make columns equal to meal data
    if (not len(list_column_names) == len(list_meal)):
        while(len(list_column_names) > len(list_meal)):
            list_column_names.pop(len(list_column_names) - 1)
        
        while(len(list_column_names) < len(list_meal)):
            list_meal.pop(len(list_meal) - 1)

    __cursor__.execute(f"INSERT INTO Meals {tuple(list_column_names)} VALUES {tuple(list_meal)}")

def get_all_table_data(table_name): #Can cause error
    """Gets all the table data using a table name
    
    Arguements: table_name (string, the name of the table)
    Returns: String (Of the data)
    """
    try:
        return __cursor__.execute(f"SELECT * FROM {table_name}").fetchall()
    except Exception as error:
        raise Exception(error)

def save_data():
    """Saves the database"""
    __connection__.commit()


if (__name__ == "__main__"):
    initialize()
else:
    initialize()


