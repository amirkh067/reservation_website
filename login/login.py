from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.debug = True

# SQLite database configuration
DB_NAME = 'login.db'

# Create a users table
with sqlite3.connect(DB_NAME) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()


@app.route('/')
def home():
    if 'username' in session:
        return f'Logged in as {session["username"]}<br><a href="/logout">Logout</a>'
    else:
        return 'Welcome!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
        
        if user is not None:
            session['username'] = user[1]  # Store the username in the session
            return redirect('/')
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
        
        if len(password) < 8 or not re.search(r'\d', password):
            flash('Password must be 8 characters with at least one number', 'error')
            return redirect('/signup')
        
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # Check if the username already exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user is not None:
                flash('Username already exists', 'error')
                return redirect('/signup')
            
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        
        flash('Signup successful! Please login.', 'success')
        return redirect('/login')
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(port=50001)