from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Flask-Mail configuration
app.config['MAIL_SERVER']='smtp.your-email-provider.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your-email@example.com' # Inserisci la tua email
app.config['MAIL_PASSWORD'] = 'your-email-password' # Inserisci la tua password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                       (username, generate_password_hash(password), email))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        db = get_db()
        # Fetch upcoming task deadlines
        tasks = db.execute('''
            SELECT title, 'task' as type FROM tasks
            WHERE user_id = ? AND date(julianday(strftime('%Y-%m-%d', 'now'))) - date(julianday(created_at)) <= 2
        ''', (session['user_id'],)).fetchall()

        # Fetch upcoming payment deadlines
        payments = db.execute('''
            SELECT description, 'payment' as type FROM payments
            WHERE date(julianday(due_date)) - date(julianday(strftime('%Y-%m-%d', 'now'))) <= 2
        ''').fetchall()

        # Fetch upcoming meetings
        meetings = db.execute('''
            SELECT title, 'meeting' as type FROM meetings
            WHERE date(julianday(date)) - date(julianday(strftime('%Y-%m-%d', 'now'))) <= 1
        ''').fetchall()

        notifications = tasks + payments + meetings
        return dict(notifications=notifications)
    return dict(notifications=None)

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/attivita')
@login_required
def attivita():
    db = get_db()
    tasks_raw = db.execute('''
        SELECT t.*, c.name as client_name
        FROM tasks t
        LEFT JOIN clients c ON t.client_id = c.id
        WHERE t.user_id = ?
    ''', (session['user_id'],)).fetchall()

    clients = db.execute('SELECT * FROM clients').fetchall()
    badges = db.execute('SELECT * FROM badges').fetchall()

    tasks = {
        'Da fare': [],
        'In corso': [],
        'Completato': []
    }

    for task in tasks_raw:
        task_dict = dict(task)
        task_badges = db.execute('SELECT b.name FROM badges b JOIN task_badges tb ON b.id = tb.badge_id WHERE tb.task_id = ?', (task['id'],)).fetchall()
        task_dict['badges'] = [b['name'] for b in task_badges]
        tasks[task['status']].append(task_dict)

    return render_template('attivita.html', tasks=tasks, clients=clients, badges=badges)

@app.route('/clients/new', methods=['POST'])
@login_required
def new_client():
    name = request.form['name']
    db = get_db()
    db.execute('INSERT INTO clients (name) VALUES (?)', (name,))
    db.commit()
    return redirect(url_for('attivita'))

@app.route('/badges/new', methods=['POST'])
@login_required
def new_badge():
    name = request.form['name']
    db = get_db()
    db.execute('INSERT INTO badges (name) VALUES (?)', (name,))
    db.commit()
    return redirect(url_for('attivita'))

@app.route('/tasks/new', methods=['POST'])
@login_required
def new_task():
    title = request.form['title']
    description = request.form.get('description')
    status = request.form['status']
    client_id = request.form.get('client_id')
    badge_ids = request.form.getlist('badge_ids')

    db = get_db()
    cursor = db.execute('INSERT INTO tasks (title, description, status, user_id, client_id) VALUES (?, ?, ?, ?, ?)',
               (title, description, status, session['user_id'], client_id))
    task_id = cursor.lastrowid

    for badge_id in badge_ids:
        db.execute('INSERT INTO task_badges (task_id, badge_id) VALUES (?, ?)', (task_id, badge_id))

    db.commit()
    return redirect(url_for('attivita'))

@app.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    status = request.form['status']
    db = get_db()
    db.execute('UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?',
               (status, task_id, session['user_id']))
    db.commit()
    return redirect(url_for('attivita'))

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, session['user_id']))
    db.commit()
    return redirect(url_for('attivita'))

@app.route('/impostazioni')
@login_required
def impostazioni():
    return render_template('impostazioni.html')

@app.route('/meeting')
@login_required
def meeting():
    db = get_db()
    meetings = db.execute('SELECT * FROM meetings ORDER BY date, time').fetchall()
    return render_template('meeting.html', meetings=meetings)

@app.route('/meetings/new', methods=['POST'])
@login_required
def new_meeting():
    title = request.form['title']
    date = request.form['date']
    time = request.form['time']
    db = get_db()
    db.execute('INSERT INTO meetings (title, date, time) VALUES (?, ?, ?)',
               (title, date, time))
    db.commit()
    return redirect(url_for('meeting'))

@app.route('/notifiche')
@login_required
def notifiche():
    db = get_db()

    # Fetch upcoming task deadlines
    tasks = db.execute('''
        SELECT title, 'task' as type FROM tasks
        WHERE user_id = ? AND date(julianday(strftime('%Y-%m-%d', 'now'))) - date(julianday(created_at)) <= 2
    ''', (session['user_id'],)).fetchall()

    # Fetch upcoming payment deadlines
    payments = db.execute('''
        SELECT description, 'payment' as type FROM payments
        WHERE date(julianday(due_date)) - date(julianday(strftime('%Y-%m-%d', 'now'))) <= 2
    ''').fetchall()

    # Fetch upcoming meetings
    meetings = db.execute('''
        SELECT title, 'meeting' as type FROM meetings
        WHERE date(julianday(date)) - date(julianday(strftime('%Y-%m-%d', 'now'))) <= 1
    ''').fetchall()

    notifications = tasks + payments + meetings

    return render_template('notifiche.html', notifications=notifications)

@app.route('/pagamenti')
@login_required
def pagamenti():
    db = get_db()
    payments_raw = db.execute('SELECT * FROM payments').fetchall()

    payments = {
        'Upcoming': [],
        'Past': []
    }

    for payment in payments_raw:
        payment_dict = dict(payment)
        payment_dict['amount'] = float(payment_dict['amount'])
        if payment_dict['status'] == 'Scheduled':
            payments['Upcoming'].append(payment_dict)
        else:
            payments['Past'].append(payment_dict)

    return render_template('pagamenti.html', payments=payments)

@app.route('/payments/new', methods=['POST'])
@login_required
def new_payment():
    description = request.form['description']
    amount = request.form['amount']
    due_date = request.form['due_date']
    status = 'Scheduled'
    db = get_db()
    db.execute('INSERT INTO payments (description, amount, due_date, status) VALUES (?, ?, ?, ?)',
               (description, amount, due_date, status))
    db.commit()

    # Send email notification
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user['email']:
        msg = Message('Payment Reminder', sender = 'your-email@example.com', recipients = [user['email']])
        msg.body = f"Hello {user['username']},\n\nThis is a reminder that a payment of ${amount} for '{description}' is due on {due_date}."
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}") # Log the error

    return redirect(url_for('pagamenti'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
