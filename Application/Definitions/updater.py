import json

class Updater():
    def __init__(self, database):
        self.database = database

    def check_update(self):
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

    def update(self):
        """Updates the database"""
        try:
            with open("Application\Definitions\database_definition.json", "r+") as file:
                data_dict = json.load(file)

                self.update_database(data_dict)
                new_data_dic = self.migrate_definitions(data_dict)

                file.seek(0)
                json.dump(new_data_dic, file, indent=4)
                file.truncate()
        except Exception as error:
            raise Exception(error)

    def migrate_definitions(self, data_dict):
        """Updates the original definition with the migration definition then deletes the migration definition"""
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

    def update_database(self, data_dict):
        """Updates the database to the new definition
        
        Parameters: data_dict (dict of the data from the database definition)
        """
        try:
            table_list = self.cursor.execute("SELECT tbl_name FROM 'main'.sqlite_master").fetchall()
            table_list = [table[0] for table in table_list]

            for table in data_dict["Migration"]["Tables"]:
                if (table_list == None):
                    #Create the table
                    self.create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                        options=data_dict["Migration"]["Tables"][table]["Options"])
                elif (table not in table_list):
                    self.create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                        options=data_dict["Migration"]["Tables"][table]["Options"])
                else:
                    #Check if the table column's are consistant with the new definition
                    table_columns = self.get_table_columns(table)
                    table_column_names = [column[0] for column in table_columns]

                    def_columns = data_dict["Migration"]["Tables"][table]["New_Columns"]

                    if (len(def_columns) < len(table_columns)):
                        raise Exception("There are more table columns than the new definition columns, Cannot downsize")
                    else:
                        #Rewrite all tables
                        mirror_table_name = self.mirror_delete_table(table)
                        self.create_table(table, column_names=data_dict["Migration"]["Tables"][table]["New_Columns"], 
                                            options=data_dict["Migration"]["Tables"][table]["Options"])

                        #Place old data into new table
                        data = self.get_all_table_data(mirror_table_name)

                        if (len(data) != 0):
                            for row in data:
                                self.cursor.execute(f"INSERT INTO {table} {tuple(table_column_names)} VALUES {tuple(row)}")

                        self.cursor.execute(f"DROP TABLE {mirror_table_name}")
                
            self.connection.commit()
        except Exception as error:
            raise Exception(error)