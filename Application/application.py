import tkinter
from tkinter import ttk

from updater import Updater
from database import Database
from window_classes import *

class Application():
    def run(self):
        self.root.mainloop()

    def __init__(self):
        self.database = Database("Food.db")
        self.updater = Updater(self.database)
        self.root = tkinter.Tk("My application")

        self.root.title("My Application")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
        try:
            self.database.check_fix_database()

            if (self.updater.check_update() == True): #can raise FileNotFoundError
                #TODO ask user if he/she wants to update the application

                self.updater.update()
                #TODO show a successful message    
        except Exception as error:
            ErrorWindow(self.root, error)
            raise Exception(error)
        
        self._configure_styles()
        self._populate_ui()

    def _configure_styles(self):
        """Adds style keywords into ttk for use by widgets"""

         #makes the background black for the main_frame
        style = ttk.Style()
        style.configure("B.TFrame", background="Black")

    def _populate_ui(self):
        """Populates the gui with frames and widgets"""

        #Add the main frame
        main_frame = ttk.Frame(self.root, relief="ridge", borderwidth=5, style="B.TFrame")
        main_frame.grid(sticky="NESW")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        tabs = ttk.Notebook(main_frame)
        tabs.grid(column=0, row=0, sticky="NESW")
        tabs.rowconfigure(0, weight=1)
        tabs.columnconfigure(0, weight=1)
        
        #Add meal frame
        meal_frame = ttk.Frame(tabs)
        tabs.add(meal_frame, text="Meal Plan")

        meal_editor = TableEditorFrame(self.root, tabs, "Meals", "meal", self.database)
        tabs.add(meal_editor.frame, text="Meal Directory")

        #Add settings frame
        settings_frame = ttk.Frame(tabs)
        tabs.add(settings_frame, text="Settings")
    
    