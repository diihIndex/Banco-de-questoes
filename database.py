import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_table(self, table_name, columns):
        columns_with_types = ', '.join(f'{col} {col_type}' for col, col_type in columns.items())
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})')
        self.connection.commit()

    def insert_data(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', tuple(data.values()))
        self.connection.commit()

    def fetch_data(self, table_name):
        self.cursor.execute(f'SELECT * FROM {table_name}')
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()