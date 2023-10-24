import math
import tkinter
from tkinter import ttk

import database
from window_classes import *

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

    meal_editor = TableEditorFrame(__root__, tabs, "Meals", "meal")
    tabs.add(meal_editor.frame, text="Meal Directory")


    def add_settings_frame(): #TODO fully implement meal frame
        settings_frame = ttk.Frame(tabs)
        tabs.add(settings_frame, text="Settings")


    add_settings_frame()

    __root__.mainloop()

#Shows a error screen and takes in a argument error (that shows in text in the window)
def show_error_window(error):
    #TODO make window size bigger and add error image and add ok button
    window = tkinter.Toplevel()
    window.title("Error!")

    #TODO make window popup in the middle of the screen (use root winfo)

    label = ttk.Label(window, text=f"{error}")
    label.grid(column=0, row=0)

if (__name__ == "__main__"):
    main()