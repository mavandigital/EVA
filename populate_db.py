import sqlite3
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

def populate():
    conn = sqlite3.connect('/tmp/database.db')
    db = conn.cursor()

    # Clear existing data
    db.execute("DELETE FROM users")
    db.execute("DELETE FROM clients")
    db.execute("DELETE FROM badges")
    db.execute("DELETE FROM tasks")
    db.execute("DELETE FROM task_badges")
    db.execute("DELETE FROM payments")
    db.execute("DELETE FROM meetings")

    # Create a user
    db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
               ('testuser', generate_password_hash('password'), 'test@example.com'))
    user_id = db.lastrowid

    # Create a client
    db.execute("INSERT INTO clients (name) VALUES (?)", ('Test Client',))
    client_id = db.lastrowid

    # Create a badge
    db.execute("INSERT INTO badges (name) VALUES (?)", ('Urgent',))
    badge_id = db.lastrowid

    # Create a task
    db.execute("INSERT INTO tasks (title, description, status, user_id, client_id) VALUES (?, ?, ?, ?, ?)",
               ('Test Task', 'This is a test task.', 'Da fare', user_id, client_id))
    task_id = db.lastrowid
    db.execute("INSERT INTO task_badges (task_id, badge_id) VALUES (?, ?)", (task_id, badge_id))

    # Create a payment due tomorrow
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    db.execute("INSERT INTO payments (description, amount, due_date, status, user_id) VALUES (?, ?, ?, ?, ?)",
               ('Test Payment Due Tomorrow', 150.00, tomorrow, 'Scheduled', user_id))

    # Create a meeting
    db.execute("INSERT INTO meetings (title, date, time, user_id) VALUES (?, ?, ?, ?)",
               ('Test Meeting', '2025-12-25', '10:00', user_id))

    conn.commit()
    conn.close()
    print("Database populated with test data. You can login with user 'testuser' and password 'password'.")

if __name__ == '__main__':
    populate()
