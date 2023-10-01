import math
import tkinter
from tkinter import ttk

import database

class Gui():
    def initialize():
        root = tkinter.Tk("My application")
        root.title("My Application")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        #makes the background black for the main_frame
        style = ttk.Style()
        style.configure("B.TFrame", background="Black")

        main_frame = ttk.Frame(root, relief="ridge", borderwidth=5, style="B.TFrame")
        main_frame.grid(sticky="NESW")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        tabs = ttk.Notebook(main_frame)
        tabs.grid(column=0, row=0, sticky="NESW")
        tabs.rowconfigure(0, weight=1)
        tabs.columnconfigure(0, weight=1)

        #Meal table: (for meals through the week)
        meal_frame = ttk.Frame(tabs)
        tabs.add(meal_frame, text="Meal Plan")

        #Configures the widgets in the data frame
        def config_data_frame():
            #Where meals will be added
            database_frame = ttk.Frame(tabs, relief="ridge", style="G.TFrame")
            tabs.add(database_frame, text="Meal Directory")
            database_frame.columnconfigure(0, weight=1)
            database_frame.rowconfigure(0, weight=1)

            #adds the meal data into the table
            def config_data_table():
                data_viewer = ttk.Treeview(database_frame, show="headings", columns=[0, 1, 2])
                data_viewer.grid(column=0, row=0, rowspan=5, sticky="NSEW")
                data_viewer.columnconfigure(0, weight=1)
                data_viewer.rowconfigure(0, weight=1)

                meal_headers = database.get_meal_column_names()
                index = 0
                for header in meal_headers:
                    data_viewer.heading(index, text=f"{header[0]}")
                    index += 1

                mealData = database.get_all_meals()
                for row in mealData:
                    data_viewer.insert('', tkinter.END, values=row)

            #Adds the options to delete, add, and so on
            def config_options():
                delete_button = ttk.Button(database_frame, text="Delete Row")
                delete_button.grid(column=1, row=0)

                add_button = ttk.Button(database_frame, text="Add Meal")
                add_button.grid(column=1, row=1, padx=10, pady=10)
                add_button.bind("<ButtonPress-1>", lambda e: show_add_meal_window(root))    

            config_data_table()
            config_options()

        config_data_frame()
        
        button = ttk.Button(meal_frame, text="Don't you dare!")
        button.bind("<ButtonPress-1>", lambda e: sample_command(root))
        button.grid(column=3, row=0)

        root.mainloop()

    #Shows a window to add meals to the database, requires the root of the window
    def show_add_meal_window(root):
        window = tkinter.Toplevel()
        window.title("Add a meal")
        window.minsize(window.winfo_reqwidth() + 50, window.winfo_reqwidth() + 50)
        #Centers and sizes window (width x height + xPos + yPos)
        window.geometry(f"200x200+{math.floor(root.winfo_screenwidth()/2 - 100)}+{math.floor(root.winfo_screenheight()/2 - 100)}")

        meal_options = database.get_meal_column_names()
        index = 0
        entries = []
        for option in meal_options:
            label = ttk.Label(window, text=f'{option}:')
            label.grid(column=0, row=index)

            entry = ttk.Entry(window)
            entry.grid(column=1, row=index)
            entries.append(entry)

            index += 1

        #Calls add_meal_database to add a meal to the database
        add_button = ttk.Button(window, text="Add Meal")
        add_button.grid(column=1, row=5)
        add_button.bind("<ButtonPress-1>", lambda e: add_meal_database(entries), sample_command(root))
    
    #Adds a meal to the database, args is the entries used to define a meal
    def add_meal_database(*args):
        meal = []

        for arg in args:
            for entry in arg:
                if (entry == ''):
                    entry = None

                meal.append(entry.get())


        database.add_meal(tuple(meal))

    def sample_command(self, root):
        root.title("You are dead to me")
