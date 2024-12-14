import sqlite3

class Sqlither:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert(self, table_name, columns, values):
        if isinstance(columns, list):
            columns = ", ".join(columns)
        print(f"INSERT INTO {table_name} ({columns}) VALUES (" +"?, "*len(values)+");")
        self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES (" +"?, "*len(values)+");", values)
        self.conn.commit()

    def select(self, table_name, columns, condition=""):
        if isinstance(columns, list):
            columns = ", ".join(columns)

        self.cursor.execute(f"SELECT {columns} FROM {table_name} {condition}")
        return self.cursor.fetchall()
    
    def update(self, table_name, columns, values, condition=""):
        if isinstance(columns, list):
            columns = ", ".join(columns)

        self.cursor.execute(f"UPDATE {table_name} SET {columns} = {values} {condition}")
        self.conn.commit()

    def __del__(self):
        self.conn.close()
