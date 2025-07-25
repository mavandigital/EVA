from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = '/tmp/database.db'

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

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/attivita')
@login_required
def attivita():
    return render_template('attivita.html', tasks={'Da fare': [], 'In corso': [], 'Completato': []}, clients=[], badges=[])


@app.route('/impostazioni')
@login_required
def impostazioni():
    return render_template('impostazioni.html', user={'username': 'test', 'email': 'test@test.com'})


@app.route('/meeting')
@login_required
def meeting():
    return render_template('meeting.html', meetings=[])

@app.route('/notifiche')
@login_required
def notifiche():
    return render_template('notifiche.html', notifications=[])

@app.route('/pagamenti')
@login_required
def pagamenti():
    return render_template('pagamenti.html', payments={'Upcoming': [], 'Past': []})


def init_db_command():
    conn = sqlite3.connect(DATABASE)
    with app.open_resource('database.py', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db_command()
    app.run(debug=True, port=8080)
