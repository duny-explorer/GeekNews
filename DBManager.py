import sqlite3


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('news.db', check_same_thread=False)

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class NewsModel:
    def __init__(self, conn):
        self.conn = conn

        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 title VARCHAR(100),
                                 content VARCHAR(1000),
                                 user_id INTEGER
                                 )''')
        cursor.close()
        self.conn.commit()

    def insert(self, title, content, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id) 
                          VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.conn.commit()

    def get(self, news_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute("SELECT id, title FROM news WHERE user_id = ?", (str(user_id)))
        else:
            cursor.execute("SELECT id, title FROM news")

        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.conn.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id),))
        cursor.close()
        self.conn.commit()

    def update(self, news_id, part, text):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE news SET {} = '{}' WHERE id = {}".format(part, text, str(news_id)))
        cursor.close()
        self.conn.commit()


class UserModel:
    def __init__(self, conn):
        self.conn = conn

        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 user_name VARCHAR(50),
                                 password_hash VARCHAR(128)
                                 )''')

        cursor.close()
        self.conn.commit()

    def get(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        row = cursor.fetchall()
        return row

    def exists(self, user_name, password_hash):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False, )
    
    def delete(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(user_id),))
        cursor.close()
        self.conn.commit()

    def insert(self, user_name, password_hash):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO users 
                             (user_name, password_hash) 
                             VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.conn.commit()
        
    def update(self, user_id, part, text):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET {} = '{}' WHERE id = {}".format(part, text, str(user_id)))
        cursor.close()
        self.conn.commit()    

