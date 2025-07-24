import requests
import re
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:8080'

def test_full_flow():
    session = requests.Session()

    # Register a new user
    print("Testing registration...")
    register_data = {
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    }
    r = session.post(f'{BASE_URL}/register', data=register_data, allow_redirects=True)
    assert r.status_code == 200
    assert 'Login' in r.text
    print("Registration successful.")

    # Log in
    print("Testing login...")
    login_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    r = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
    assert r.status_code == 200
    assert 'Overview' in r.text
    print("Login successful.")

    # Add a new task
    print("Testing new task...")
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task.',
        'status': 'Da fare'
    }
    r = session.post(f'{BASE_URL}/tasks/new', data=task_data, allow_redirects=True)
    assert r.status_code == 200
    assert 'Test Task' in r.text
    print("New task added successfully.")

    # Add a new payment
    print("Testing new payment...")
    payment_data = {
        'description': 'Test Payment',
        'amount': '100.00',
        'due_date': '2025-12-31'
    }
    r = session.post(f'{BASE_URL}/payments/new', data=payment_data, allow_redirects=True)
    assert r.status_code == 200
    assert 'Test Payment' in r.text
    print("New payment added successfully.")

    # Add a new meeting
    print("Testing new meeting...")
    meeting_data = {
        'title': 'Test Meeting',
        'date': '2025-12-25',
        'time': '10:00'
    }
    r = session.post(f'{BASE_URL}/meetings/new', data=meeting_data, allow_redirects=True)
    assert r.status_code == 200
    assert 'Test Meeting' in r.text
    print("New meeting added successfully.")

    # Check notifications
    print("Testing notifications...")
    r = session.get(f'{BASE_URL}/notifiche')
    assert r.status_code == 200
    assert 'Test Task' in r.text
    assert 'Test Payment' in r.text
    assert 'Test Meeting' in r.text
    print("Notifications are working.")

    print("\nAll tests passed!")

if __name__ == '__main__':
    test_full_flow()
