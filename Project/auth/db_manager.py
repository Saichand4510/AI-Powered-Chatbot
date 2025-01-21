import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_users_table()

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_user(self, username, email, password):
        try:
            query = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
            self.conn.execute(query, (username, email, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, email, password):
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        cursor = self.conn.execute(query, (email, password))
        result = cursor.fetchone()  
        if result is not None:  
          return result[0]  
        else:
          return None
