import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    email TEXT
                )''')
    print("Table 'users' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    print("Table 'tasks' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    due_date TEXT,
                    status TEXT NOT NULL
                )''')
    print("Table 'payments' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL
                )''')
    print("Table 'meetings' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    print("Table 'notifications' created successfully")

    conn.close()

if __name__ == '__main__':
    init_db()
