import sqlite3
import json

def initialize():
    global __connection__ 
    __connection__ = sqlite3.connect("Food.db")

    global __cursor__
    __cursor__ = __connection__.cursor()

def save_database():
    __connection__.commit()

def check_fix_database(): #Checks the database and fixs any problems
    """Checks the database and fixs any problems that occur"""
    #TODO add error handling and return the error

    with open("Application\Definitions\database_definition.json", "r") as file:
        data_dict = json.load(file)

        result = check_database_definition(data_dict)

def check_database_definition(data_dict): # TODO Error handling
    """checks if the database is equal to the definition
    
    Returns: String (any error that occured
    )"""

    table_list = __cursor__.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
    table_list = [table[0] for table in table_list]

    for table in data_dict["Tables"]:
        if (table not in table_list):
            result = create_table(table, column_names=data_dict["Tables"][table]["Columns"], options=data_dict["Tables"][table]["Options"])

            if (result != True):
                return result
        else:
            #Check if the table column's are consistant with the definitions
            table_columns = get_table_columns(table)
            def_columns = data_dict["Tables"][table]["Columns"]

            if (table_columns == False):
               return "Could not get the table columns!"

            if (len(def_columns) != len(table_columns)):
                return "Tables lengths are not consistant!"
            else:
                #Check if the names are the same
                for x in range(0, len(def_columns)):
                    if (table_columns[x] != def_columns[x]):
                         return"Column names don't match!"
            
    __connection__.commit()

def check_update():
    """Checks if there's an update available inside the definition.json
    
    Returns False (No update)
            True (update)
    """
    with open("Application\Definitions\database_definition.json", "r+") as file:
        data_dict = json.load(file)

        if ("Migration" in data_dict.keys()):
            return True
        else:
            return False

def update():
    """Updates the database
    
    Returns String (of the error if it occured)
            True (Successful!)
    """

    with open("Application\Definitions\database_definition.json", "r+") as file:
        data_dict = json.load(file)

        result = update_database(data_dict)

        if (result == True):
            new_data_dic = migrate_definitions(data_dict)

            file.seek(0)
            json.dump(new_data_dic, file, indent=4)
            file.truncate()

            return True
        else:
            print(result)
            return result

def migrate_definitions(data_dict): #will migrate the migration to the definition
    data_dict["Version"] = data_dict["Migration"]["Version"]
    data_dict["Tables"] = data_dict["Migration"]["Tables"]

    for table in data_dict["Tables"]:
        data_dict["Tables"][table]["Columns"] = data_dict["Migration"]["Tables"][table]["New_Columns"]
        data_dict["Tables"][table]["Options"] = data_dict["Migration"]["Tables"][table]["Options"]
        del data_dict["Tables"][table]["New_Columns"]
        del data_dict["Tables"][table]["Old_Columns"]

    del data_dict["Migration"]

    return data_dict 

def update_database(data_dict):
    """Updates the database to the new definition
    
    Parameters: data_dict (dict of the data from the database definition)
    Returns: True (If successful)
             String (If there's an error)
    """
    table_list = __cursor__.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
    table_list = [table[0] for table in table_list]

    for table in data_dict["Migration"]["Tables"]:
        if (table_list == None):
            #Create the table
            result = create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                  options=data_dict["Migration"]["Tables"][table]["Options"])
            if (result != True):
                return result
        elif (table not in table_list):
            result = create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                  options=data_dict["Migration"]["Tables"][table]["Options"])
            if (result != True):
                return result
        else:
            #Check if the table column's are consistant with the new definition
            table_columns = get_table_columns(table)
            def_columns = data_dict["Migration"]["Tables"][table]["New_Columns"]

            # if (table_columns.keys() == def_columns.keys()):
            #     continue #New definition must be the same as the old one #TODO what about options though?

            if (table_columns == False):
                return "An error went wrong while getting the table columns" 
            
            if (len(def_columns) < len(table_columns)):
                return "There are more table columns than the new definition columns, Cannot downsize"
            else: #TODO catch possible errors
                #Rewrite all tables
                mirror_table_name = mirror_delete_table(table)
                result = create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                      options=data_dict["Migration"]["Tables"][table]["Options"])

                if (result != True):
                    return result

                #Place old data into new table
                data = get_all_table_data(mirror_table_name)

                try: 
                    if (len(data) != 0):
                        __cursor__.execute(f"INSERT INTO {table} {tuple(data)} VALUES {tuple(table_columns)}")

                    __cursor__.execute(f"DROP TABLE {mirror_table_name}")
                except Exception as e:
                    return e
            
    __connection__.commit()
    return True

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

        return True
    except Exception as error:
        return error

def get_table_columns(table_name):
    """Returns the columns from a table
    
    Returns 2D Tuple ('Name', 'Type')
    """
    #TODO add try catch and return True if operation is successful
    column_names = __cursor__.execute(f"SELECT name, type FROM PRAGMA_TABLE_INFO('{table_name}')").fetchall()

    name_list = [name for name in column_names]
    return tuple(name_list)

#Creates a mirror of a table and then deletes it. This returns the new_table_name or False if unsuccessful
def mirror_delete_table(table_name): #TODO Error catching
    """reates a mirror of a table and then deletes it. This returns the new_table_name or False if unsuccessful
    
        Arguements: table_name (string)
    """
    column_names = [col_def[0] for col_def in get_table_columns(table_name)]

    table_data = get_all_table_data(table_name)
    new_table_name = table_name + "_Mirror"

    didSucceed = create_table(new_table_name, column_names)

    if (not didSucceed or column_names == False or table_data == False):
        return False
    
    for row in table_data:
        __cursor__.execute(f"INSERT INTO {new_table_name} {tuple(column_names)} VALUES {tuple(str(element) for element in row)}")
    
    __cursor__.execute(f"DROP TABLE {table_name}")

    return new_table_name

#adds a meal to database where meal is a list or tuple of the columns in the meal table
def add_meal(meal): #TODO make this modular, make this add data into table
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

#Get's all the data from a table. Arguments: table_name (string). Returns a tuple of the data, False if the operation is unsuccessful
def get_all_table_data(table_name): #TODO documentation
    try:
        return __cursor__.execute(f"SELECT * FROM {table_name}").fetchall()
    except Exception as e:
        return e


def save_data():
    pass #TODO Save all changes made to the database


if (__name__ == "__main__"):
    initialize()
else:
    initialize()


