from flask import Flask, render_template, request, jsonify, redirect
import sqlite3

login_app = Flask(__name__)

# Create the users table if it doesn't exist
def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Create the user table on application startup
create_user_table()

@login_app.route('/')
def home():
    return render_template('index.html')

@login_app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Query the database to retrieve the user's credentials
    cursor.execute('''
        SELECT password FROM users
        WHERE username = ?
    ''', (username,))
    
    result = cursor.fetchone()

    if result and result[0] == password:
        # Redirect to index.html
        return redirect('/index.html')
    else:
        # Incorrect credentials, display an error message
        return render_template('login.html', error='Incorrect username or password')

@login_app.route('/index.html')
def index():
    # Add code to handle the authenticated user's request
    return render_template('index.html')
