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

    conn.execute('''CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )''')
    print("Table 'clients' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )''')
    print("Table 'badges' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    user_id INTEGER,
                    client_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(client_id) REFERENCES clients(id)
                )''')
    print("Table 'tasks' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS task_badges (
                    task_id INTEGER,
                    badge_id INTEGER,
                    PRIMARY KEY (task_id, badge_id),
                    FOREIGN KEY(task_id) REFERENCES tasks(id),
                    FOREIGN KEY(badge_id) REFERENCES badges(id)
                )''')
    print("Table 'task_badges' created successfully")


    conn.execute('''CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    due_date TEXT,
                    status TEXT NOT NULL,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    print("Table 'payments' created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
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
