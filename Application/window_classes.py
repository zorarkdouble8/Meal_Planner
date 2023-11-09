import math
from tkinter import Tk
from tkinter import ttk
import tkinter

class Window():
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent

class ErrorWindow(Window):
    def __init__(self, root, error_message):
        """Shows an error window with an error message
        
        Arguments: root (the root of the application)
                   error_message (the message to show in the application)"""
        Window.__init__(self, root, None)
        self.error = error_message
        
        self.window = tkinter.Toplevel()
        self.window.title("Error!")

        self._center_and_size_window()
        self._add_message()
        
    def _center_and_size_window(self):
        """Centers the window and sizes it"""
        self.window.minsize(self.window.winfo_reqwidth() + 50, self.window.winfo_reqwidth() + 50)
        #Centers and sizes window (width x height + xPos + yPos)
        self.window.geometry(f"200x200+{math.floor(self.root.winfo_screenwidth()/2 - 100)}+{math.floor(self.root.winfo_screenheight()/2 - 100)}")

    def _add_message(self):
        """Adds a label with the error message inside it"""
        label = ttk.Label(self.window, text=f"{self.error}")
        label.grid(column=0, row=0)
        

class TableEditorFrame(Window):
    def __init__(self, root, parent, table_name, object_message, database):
        """Adds a table editor frame to a parent obj
        
        Arguments: root (the root of the application)
                    parent (the parent this frame will attach to)
                    table_name (the table this editor will show)
                    object_message (a string that customizes the option message IE: add a 'meal', add a <object_message>)
        """
        Window.__init__(self, root, parent)

        self.table_name = table_name
        self.object_message = object_message.lower()

        self.frame = ttk.Frame(self.parent)
        self.options_frame = ttk.Frame(self.frame)
        self.options_frame.grid(column=1, row=0, sticky="N")

        self.database = database

        try:
            self.columns = self.database.get_table_columns(table_name)
            self.data = self.database.get_all_table_data(table_name)
        except Exception as error:
            raise Exception(error)
        
        self._configure_data_viewer()
        self._configure_options()

    def _configure_data_viewer(self):
        """Configures the widgets"""
        self.data_viewer = ttk.Treeview(self.frame, show="headings", columns=self.columns)
        self.data_viewer.grid(column=0, row=0, rowspan=5, sticky="NSEW")
        self.data_viewer.columnconfigure(0, weight=1)
        self.data_viewer.rowconfigure(0, weight=1)

        self._populate_data_viewer()

    def _populate_data_viewer(self):
        """Adds the table data to the data viewer"""
        self.header = []

        for index, column in enumerate(self.columns):
            self.data_viewer.heading(index, text=f"{column[0]}")
            self.header.append(column[0]) #for use in other methods

        for row in self.data:
            self.data_viewer.insert('', tkinter.END, values=row)

    def _configure_options(self):
        """Adds the options to the side of the data viewer"""
        info_label = ttk.Label(self.options_frame, text="Options")
        info_label.grid(column=0, row=0)

        delete_button = ttk.Button(self.options_frame, text="Delete Row")
        delete_button.grid(column=0, row=3)
        delete_button.bind("<ButtonPress-1>", lambda e: self.delete_row_from_database_viewer())

        edit_button = ttk.Button(self.options_frame, text="Edit Row")
        edit_button.grid(column=0, row=2)
        edit_button.bind("<ButtonPress-1>", lambda e: self.edit_row_from_database_viewer())

        add_button = ttk.Button(self.options_frame, text=f"Add {self.object_message.title()}")
        add_button.grid(column=0, row=1)
        add_button.bind("<ButtonPress-1>", lambda e: self.show_window_editor()) 

        save_button = ttk.Button(self.options_frame, text="Save")
        save_button.grid(column=0, row=4)
        save_button.bind("<ButtonPress-1>", lambda e: self.database.save_database())
        
    def delete_row_from_database_viewer(self):
        """Deletes a selected row from the database viewer"""
        try:
            row_selection = self.data_viewer.focus() #can case Index error

            data = self.data_viewer.item(row_selection)
            values = data["values"]
            column_index = self.header.index("ID") #can cause value error

            self.database.delete_table_data(values[column_index], self.table_name)

            self.data_viewer.delete(row_selection)
        except IndexError as error:
            raise IndexError(error, "No row may be selected")
        except ValueError as error:
            raise ValueError(error, "Table columns don't have an id header!")
        except Exception as error:
            raise Exception(error)

    def edit_row_from_database_viewer(self):
        """Gets the row to be editted and shows the meal window editor to edit the row"""
        row_info = self.data_viewer.item(self.data_viewer.focus())
        self.show_window_editor(row_info["values"])

    def show_window_editor(self, row_data=None):
        """Shows a window to add meals to the self.database, requires the root of the window and the data viewer for the meal table"""
        window = tkinter.Toplevel()

        if (row_data == None or len(row_data) == 0):
            window.title(f"Add a {self.object_message.title()}")
        else:
            window.title(f"Edit a {self.object_message.title()}")

        window.minsize(window.winfo_reqwidth() + 50, window.winfo_reqwidth() + 50)
        #Centers and sizes window (width x height + xPos + yPos)
        window.geometry(f"200x200+{math.floor(self.root.winfo_screenwidth()/2 - 100)}+{math.floor(self.root.winfo_screenheight()/2 - 100)}")

        entries = []
        labels = []

        for index, column in enumerate(self.columns):
            column_name = column[0]
            type = column[1]

            label = ttk.Label(window, text=f'{column_name}:')
            label.grid(column=0, row=index)

            if (type == "TEXT"):
                entry = ttk.Entry(window)
                if not (row_data == None or len(row_data) == 0):
                    entry.insert(0, row_data[index])

                entry.grid(column=1, row=index)
                entries.append(entry)
                labels.append(label)
            elif (column_name == "ID"):
                if not (row_data == None or len(row_data) == 0):
                    text = row_data[index]
                else:
                    text = "Automatically Generated"
                id_label = ttk.Label(window, text=text)
                id_label.grid(column=1, row=index)

        if (row_data == None or len(row_data) == 0):
            add_button = ttk.Button(window, text=f"Add {self.object_message}")
            add_button.bind("<ButtonPress-1>", lambda e: ((self.add_row_database(labels, entries), self._refresh_data_viewer()), window.destroy()))
        else:
            add_button = ttk.Button(window, text=f"Save {self.object_message}")
            add_button.bind("<ButtonPress-1>", lambda e: ((self.modify_row_database(id_label, labels, entries), self._refresh_data_viewer()), window.destroy()))

        add_button.grid(column=1, sticky="S")
            
    def add_row_database(self, labels, entries):
        """Adds a row to the database and then refreshes the database viewer
    
        Arguements: labels (the label associated with the entry)
                    entries (entries used for user input)
        """
        meal = []

        for index, entry in enumerate(entries):
            text = entry.get()
            if (text == ''):
                text = "None"

            meal.append((labels[index].cget("text").replace(":", ""), text))

        self.database.add_row_to_table(self.table_name, meal)

    def modify_row_database(self, id_label, labels, entries):
        """Modifies and existing row in the database
        
        Arguements: labels (the label associated with the entry)
                    entries (entries used for user input)
        """
        meal = []
        for index, entry in enumerate(entries):
            text = entry.get()
            if (text == ''):
                text = "None"

            meal.append((labels[index].cget("text").replace(":", ""), text))

        self.database.update_row_to_table(self.table_name, id_label.cget("text"), meal)
            
    def _refresh_data_viewer(self):
        """Gets all the data from the database to refesh the database viewer"""
        try:
            self.data = self.database.get_all_table_data(self.table_name)
        except Exception as error:
            raise Exception(error)
        
        self.data_viewer.delete(*self.data_viewer.get_children())
        self._populate_data_viewer()