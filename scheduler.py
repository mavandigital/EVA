import sqlite3
from flask import Flask
from flask_mail import Mail, Message
from datetime import date, timedelta

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.your-email-provider.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

DATABASE = '/tmp/database.db'

def send_reminders():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    payments_due = db.execute("SELECT p.*, u.username, u.email FROM payments p JOIN users u ON p.user_id = u.id WHERE p.due_date = ? AND p.status = 'Scheduled'", (tomorrow,)).fetchall()

    with app.app_context():
        for payment in payments_due:
            if payment['email']:
                msg = Message(
                    "Payment Reminder",
                    sender='your-email@example.com',
                    recipients=[payment['email']]
                )
                msg.body = f"Hello {payment['username']},\n\nThis is a reminder that a payment of ${payment['amount']} for '{payment['description']}' is due tomorrow, {payment['due_date']}."
                try:
                    mail.send(msg)
                    print(f"Sent reminder to {payment['email']} for payment ID {payment['id']}")
                except Exception as e:
                    print(f"Error sending email to {payment['email']}: {e}")

    conn.close()

if __name__ == '__main__':
    send_reminders()
