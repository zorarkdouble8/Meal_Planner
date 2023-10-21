import math
import tkinter
from tkinter import ttk

import database

def main():
    global __root__
    __root__ = tkinter.Tk("My application")
    __root__.title("My Application")
    __root__.columnconfigure(0, weight=1)
    __root__.rowconfigure(0, weight=1)

    try:
        database.check_fix_database() #TODO if error show window

        if (database.check_update() == True): #can raise FileNotFoundError
            #TODO ask user if he/she wants to update the application

            if (database.update() == True):
                #TODO show a successful message
                pass
    except Exception as error:
        raise Exception(error) #TODO Add error window to show user something went wrong

    #makes the background black for the main_frame
    style = ttk.Style()
    style.configure("B.TFrame", background="Black")

    main_frame = ttk.Frame(__root__, relief="ridge", borderwidth=5, style="B.TFrame")
    main_frame.grid(sticky="NESW")
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    tabs = ttk.Notebook(main_frame)
    tabs.grid(column=0, row=0, sticky="NESW")
    tabs.rowconfigure(0, weight=1)
    tabs.columnconfigure(0, weight=1)
    
    def add_meal_frame():#TODO fully implement meal frame
        meal_frame = ttk.Frame(tabs)
        tabs.add(meal_frame, text="Meal Plan")

    add_meal_frame()

    #Configures the widgets in the data frame
    def config_data_frame():
        #Where meals will be added
        database_frame = ttk.Frame(tabs, relief="ridge", style="G.TFrame")
        tabs.add(database_frame, text="Meal Directory")
        database_frame.columnconfigure(0, weight=1)
        database_frame.rowconfigure(0, weight=1)

        #adds the meal data into the table
        def config_data_table():
            global data_viewer
            meal_columns = database.get_table_columns("Meals")

            data_viewer= ttk.Treeview(database_frame, show="headings", columns=[index for index, header in enumerate(meal_columns)])
            data_viewer.grid(column=0, row=0, rowspan=5, sticky="NSEW")
            data_viewer.columnconfigure(0, weight=1)
            data_viewer.rowconfigure(0, weight=1)

        
            for index, column in enumerate(meal_columns):
                data_viewer.heading(index, text=f"{column[0]}")

            mealData = database.get_all_table_data("Meals") #TODO add if it's false *Error
            
            for row in mealData:
                data_viewer.insert('', tkinter.END, values=row) 

        #Adds the options to delete, add, and so on
        def config_options():
            options_frame = ttk.Frame(database_frame)
            options_frame.grid(column=1, row=0, sticky="N")

            info_label = ttk.Label(options_frame, text="Options")
            info_label.grid(column=0, row=0)

            delete_button = ttk.Button(options_frame, text="Delete Row")
            delete_button.grid(column=0, row=3)
            delete_button.bind("<ButtonPress-1>", lambda e: delete_row_from_database_viewer())

            edit_button = ttk.Button(options_frame, text="Edit Row")
            edit_button.grid(column=0, row=2)
            edit_button.bind("<ButtonPress-1>", lambda e: edit_row_from_database_viewer())

            add_button = ttk.Button(options_frame, text="Add Meal")
            add_button.grid(column=0, row=1)
            add_button.bind("<ButtonPress-1>", lambda e: meal_window_editor()) 

            save_button = ttk.Button(options_frame, text="Save")
            save_button.grid(column=0, row=4)
            save_button.bind("<ButtonPress-1>", lambda e: database.save_data())

        config_data_table()
        config_options()

    #TODO I would like these methods to be up on top of the functions
    config_data_frame()  

    def add_settings_frame(): #TODO fully implement meal frame
        settings_frame = ttk.Frame(tabs)
        tabs.add(settings_frame, text="Settings")


    add_settings_frame()

    __root__.mainloop()

#Gets the row to be edditted and shows the meal window editor to edit the row
def edit_row_from_database_viewer():
    row_info = data_viewer.item(data_viewer.focus())
    meal_window_editor(row_info["values"])
   
#Deletes a selected row from the database viewer
def delete_row_from_database_viewer():
    try:
        row_selection = data_viewer.focus()
        data_viewer.delete(row_selection)
    except:
        show_error_window("No row selected!")

#Shows a error screen and takes in a argument error (that shows in text in the window)
def show_error_window(error):
    #TODO make window size bigger and add error image and add ok button
    window = tkinter.Toplevel()
    window.title("Error!")

    #TODO make window popup in the middle of the screen (use root winfo)

    label = ttk.Label(window, text=f"{error}")
    label.grid(column=0, row=0)

#Shows a window to add meals to the database, requires the root of the window and the data viewer for the meal table
def meal_window_editor(meal_info = None):
    window = tkinter.Toplevel()

    if (meal_info == None or len(meal_info) == 0):
        window.title("Add a meal")
    else:
        window.title("Edit a meal")

    window.minsize(window.winfo_reqwidth() + 50, window.winfo_reqwidth() + 50)
    #Centers and sizes window (width x height + xPos + yPos)
    window.geometry(f"200x200+{math.floor(__root__.winfo_screenwidth()/2 - 100)}+{math.floor(__root__.winfo_screenheight()/2 - 100)}")

    meal_columns = database.get_table_columns("Meals")

    entries = []
    labels = []

    for index, column in enumerate(meal_columns): #TODO have entries be type based on the column
        column_name = column[0]
        type = column[1]

        label = ttk.Label(window, text=f'{column_name}:')
        label.grid(column=0, row=index)

        if (type == "TEXT"):
            entry = ttk.Entry(window)
            entry.grid(column=1, row=index)
            entries.append(entry)
            labels.append(label)
        elif (column_name == "ID"):
            id_label = ttk.Label(window, text="Automatically Generated")
            id_label.grid(column=1, row=index)

    if (meal_info == None or len(meal_info) == 0):
        add_button = ttk.Button(window, text="Add Meal")
        add_button.bind("<ButtonPress-1>", lambda e: (add_meal(labels, entries), window.destroy()))
    else:
        add_button = ttk.Button(window, text="Save Meal")
        add_button.bind("<ButtonPress-1>", lambda e: (edit_meal_database(entries), window.destroy()))

    add_button.grid(column=1, sticky="S")
    
def edit_meal_database(*args): 
    pass #TODO solve index problem

def add_meal(labels, entries): #TODO error catching
    """Adds a meal to the database and then refreshes the database viewer
    
    Arguements: labels (the label associated with the entry)
                entries (entries used for user input)
    """
    meal = []

    for index, entry in enumerate(entries):
        text = entry.get()
        if (text == ''):
            text = "None"

        meal.append((labels[index].cget("text").replace(":", ""), text))

    database.add_row_to_table("Meals", meal)
    add_meal_to_database_viewer(meal)

#refreshes the database viewer widget
def add_meal_to_database_viewer(meal):
    data_viewer.insert('', tkinter.END, values=meal)

if (__name__ == "__main__"):
    main()