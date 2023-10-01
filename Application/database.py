import sqlite3

def initialize():
    global __connection__ 
    __connection__ = connection = sqlite3.connect("Food.db")

    global __cursor__
    __cursor__ = __connection__.cursor()

def create_meal_table():
    __cursor__.execute("CREATE TABLE Meals(Name, Servings, Ingredients)")

def add_unique_index_Column(tableName):
    #__cursor__.execute("ALTER TABLE Meals ADD Unique_Index INTEGER AUTO_INCREMENT")
    #__cursor__.execute("CREATE UNIQUE INDEX Meal_Index ON Meals(Unique_Index)")
    __cursor__.execute("ALTER TABLE Meals DROP Unique_Index")

#adds a meal to database where meal is a list or tuple of the columns in the meal table
def add_meal(meal):
    column_names = get_meal_column_names()

    list_meal = list(meal)
    list_column_names = list(column_names)
    
    #Make columns equal to meal data
    if (not len(list_column_names) == len(list_meal)):
        while(len(list_column_names) > len(list_meal)):
            list_column_names.pop(len(list_column_names) - 1)
        
        while(len(list_column_names) < len(list_meal)):
            list_meal.pop(len(list_meal) - 1)

    __cursor__.execute(f"INSERT INTO Meals {tuple(list_column_names)} VALUES {tuple(list_meal)}")

def get_meal(mealName):
    pass #TODO

def get_all_meals():
    try:
        return __cursor__.execute("SELECT * FROM Meals").fetchall()   
    except:
        #Table might not exist
        try:
            create_meal_table()
            return __cursor__.execute("SELECT * FROM Meals").fetchall()  
        except:
            pass #TODO Error window? (don't know what the error might be)

def save_data():
    pass #TODO Save all changes made to the database

#Returns a tuple of column names
def get_meal_column_names():
    column_names = __cursor__.execute("SELECT name FROM PRAGMA_TABLE_INFO('Meals')").fetchall()
    
    name_list = [name[0] for name in column_names]

    return tuple(name_list)


if (__name__ == "__main__"):
    initialize()
    add_unique_index_Column(None)
else:
    initialize()

#cursor.execute("CREATE TABLE Meals(Name, Servings, Ingredients)")
#cursor.execute("INSERT INTO Meals(Name, Servings) VALUES ('Test', '4')")


