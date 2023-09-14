from flask import Flask, render_template, request, redirect, session, flash, jsonify, make_response
import sqlite3
import re
from datetime import datetime
import threading
from werkzeug.local import Local
import pandas as pd
from flask import make_response
from io import BytesIO
import json
import logging
import threading
import random
import string


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'
app.debug = True

# SQLite database configuration
LOGIN_DB_NAME = 'login.db'
USERS_DB_NAME = 'users.db'

# Create a thread-local storage for the database connection
login_connection_local = Local()
users_connection_local = Local()

def get_login_db():
    if not hasattr(login_connection_local, 'connection'):
        login_connection_local.connection = sqlite3.connect(LOGIN_DB_NAME)
    return login_connection_local.connection

def get_users_db():
    if not hasattr(users_connection_local, 'connection'):
        users_connection_local.connection = sqlite3.connect(USERS_DB_NAME)
    return users_connection_local.connection

# Create the users table in login.db if it doesn't exist
with sqlite3.connect(LOGIN_DB_NAME) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()

# Create the user table in users.db if it doesn't exist
"""def create_user_table():
    conn = get_users_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            address TEXT NOT NULL,
            date_added TEXT,
            time_added TIME,
            hali_sayisi INTEGER,
            phone_number TEXT
        )
    ''')
    conn.commit()"""

def create_user_table():
    conn = get_users_db()
    cursor = conn.cursor()
    
    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            username TEXT,
            date_added TEXT,
            time_added TIME,
            hali_sayisi INTEGER,
            phone_number TEXT,
            Address TEXT,
            fiyat INTEGER
        )
    ''')
    
    # Add the time_added column if it doesn't exist
    cursor.execute('''
        PRAGMA table_info(users)
    ''')
    
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'order_id' not in column_names:
        cursor.execute('''
            ALTER TABLE users
            ADD COLUMN order_id TEXT
        ''')
    
    conn.commit()

# Create the users table on application startup
create_user_table()



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
        
        with sqlite3.connect(LOGIN_DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
        
        if user is not None:
            session['username'] = user[1]  # Store the username in the session
            return redirect('/main.html')  # Redirect to index.html
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login')
    
    return render_template('login.html')

@app.route('/Adminlogin', methods=['GET', 'POST'])
def Adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(LOGIN_DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
        
        if user is not None:
            session['username'] = user[1]  # Store the username in the session
            return redirect('/main.html')  # Redirect to index.html
        else:
            flash('Invalid username or password', 'error')
            return redirect('/Adminlogin')
    
    return render_template('Adminlogin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        # Only allow the admin user to access the signup page
        if session['username'] != 'aamirkhan34':
            flash('Access denied. Only the admin can access this page.', 'error')
            return redirect('/')

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
        
        with sqlite3.connect(LOGIN_DB_NAME) as conn:
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


@app.route('/main.html')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/index')
def index():
    return render_template('index.html')

"""@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    hali_sayisi = int(request.form['hali_sayisi'])
    phone_number = request.form['phone_number']
    today = date.today().strftime("%Y-%m-%d")

    conn = get_users_db()
    cursor = conn.cursor()

    # Insert the user data into the database
    cursor.execute('''
        INSERT INTO users (username, email, date_added, hali_sayisi, phone_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, email, today, hali_sayisi, phone_number))
    conn.commit()

    # Return a JSON response indicating success
    return jsonify({'message': 'User added successfully!'})
    """
def generate_order_id():
    static_prefix = "EDHY"
    random_suffix = ''.join(random.choices(string.digits, k=6))
    order_id = static_prefix + random_suffix
    return order_id


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    address = request.form['address']
    hali_sayisi = int(request.form['hali_sayisi'])
    phone_number = request.form['phone_number']
    now = datetime.now()
    fiyat = request.form['fiyat']

    order_id = generate_order_id()

    conn = get_users_db()
    cursor = conn.cursor()

    # Insert the user data into the database
    cursor.execute('''
        INSERT INTO users (order_id, username, address, date_added, time_added, hali_sayisi, phone_number, fiyat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, username, address, now.date().strftime('%Y-%m-%d'), now.time().strftime('%H:%M:%S'), hali_sayisi, phone_number, fiyat))
    conn.commit()

    # Return a JSON response indicating success
    response = {'message': 'Şipariş Oluşturuldu!', 'order_id': order_id}
    print(json.dumps(response, indent=4))
    return jsonify(response)

"""@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    address = request.form['address']
    hali_sayisi = int(request.form['hali_sayisi'])
    phone_number = request.form['phone_number']
    now = datetime.now()
    fiyat = request.form['fiyat']

    conn = get_users_db()
    cursor = conn.cursor()

    # Insert the user data into the database
    cursor.execute('''
        INSERT INTO users (username, address, date_added, time_added, hali_sayisi, phone_number, fiyat)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, address, now.date().strftime('%Y-%m-%d'), now.time().strftime('%H:%M:%S'), hali_sayisi, phone_number, fiyat))
    conn.commit()

    # Return a JSON response indicating success
    return jsonify({'message': 'User added successfully!'})"""



"""@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_date = request.form['search_date']
        
        conn = get_users_db()
        cursor = conn.cursor()
        
        # Convert search_date to datetime object
        try:
            search_date = datetime.datetime.strptime(search_date, '%Y-%m-%d').date()
        except ValueError:
            search_date = None
        
        # Query the database to retrieve matching users
        if search_date:
            cursor.execute('''
                SELECT * FROM users
                WHERE (LOWER(username) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?))
                      AND date_added = ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', search_date))
        else:
            cursor.execute('''
                SELECT * FROM users
                WHERE LOWER(username) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?)
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        app.logger.debug(f"Results: {results}")  # Debugging statement

        return render_template('search_results.html', results=results)

    return render_template('search.html')"""


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_date = request.form['search_date']

        conn = get_users_db()
        cursor = conn.cursor()

        # Convert search_date to datetime object
        try:
            search_date = datetime.strptime(search_date, '%Y-%m-%d').date()
        except ValueError:
            search_date = None

        # Query the database to retrieve matching users
        if search_date and not search_term:
            cursor.execute('''
                SELECT * FROM users
                WHERE date_added = ?
            ''', (search_date,))
        elif search_term and not search_date:
            cursor.execute('''
                SELECT * FROM users
                WHERE LOWER(username) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?) OR LOWER(fiyat) LIKE LOWER(?) OR LOWER(order_id) LIKE LOWER(?)
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        elif search_date and search_term:
            cursor.execute('''
                SELECT * FROM users
                WHERE (LOWER(username) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?) OR LOWER(fiyat) LIKE LOWER(?)) OR LOWER(order_id) LIKE LOWER(?)
                      AND date_added = ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', search_date))

        else:
            cursor.execute('SELECT * FROM users')

        results = cursor.fetchall()
        app.logger.debug(f"Results: {results}")  # Debugging statement

        # Calculate the sum of the "Hali Sayısı" column
        sum_hali_sayisi = sum(result[5] for result in results)  # Ignore the 1st row

        # Calculate the sum of the "Fiyat" column
        sum_fiyat = sum(result[8] for result in results)  # Ignore the 1st row

        app.logger.debug(f"Sum Hali Sayısı: {sum_hali_sayisi}")  # Debugging statement
        app.logger.debug(f"Sum Fiyat: {sum_fiyat}")  # Debugging statement

        return render_template('search_results.html', results=results, sum_hali_sayisi=sum_hali_sayisi, sum_fiyat=sum_fiyat)
    else:
        return render_template('search.html')







# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


@app.route('/download_excel', methods=['POST'])
def download_excel():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_date = request.form['search_date']
        
        conn = get_users_db()
        cursor = conn.cursor()
        
        # Convert search_date to datetime object
        try:
            search_date = datetime.strptime(search_date, '%Y-%m-%d').date()
        except ValueError:
            search_date = None
        
        # Query the database to retrieve matching users
        if search_date and not search_term:
            cursor.execute('''
                SELECT * FROM users
                WHERE date_added = ?
            ''', (search_date,))
        elif search_term and not search_date:
            cursor.execute('''
                SELECT * FROM users
                WHERE LOWER(username) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?) OR LOWER(fiyat) LIKE LOWER(?) OR LOWER(order_id) LIKE LOWER(?)
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        elif search_date and search_term:
            cursor.execute('''
                SELECT * FROM users
                WHERE (LOWER(username) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR
                      LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?) OR LOWER(fiyat) LIKE LOWER(?)) OR LOWER(order_id) LIKE LOWER(?)
                      AND date_added = ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%',f'%{search_term}%', search_date))
            
        else:
            cursor.execute('SELECT * FROM users')
        
        results = cursor.fetchall()
        app.logger.debug(f"Results: {results}")  # Debugging statement

        # Add headings to the first row
        headings = ['ID', 'Siparis No', 'Name', 'Date Added', 'Time Added', 'Hali Sayisi', 'Phone Number', 'Address', 'Fiyat']
        results.insert(0, headings)

        # Convert results to a pandas DataFrame
        df = pd.DataFrame(results)
        
        # Calculate the sum of the "Hali Sayisi" column, ignoring the first row
        sum_hali_sayisi = df.iloc[1:, 5].sum()
        
        # Create a DataFrame for the total row
        total_row = pd.DataFrame([['Total Hali Sayisi', '', sum_hali_sayisi, '', '', '', '', '', '']],
                         columns=df.columns)

        sum_fiyat = df.iloc[1:, 8].sum()

        #total_fiyat = pd.DataFrame([['Total Fiyat', '', '', sum_fiyat, '', '', '', '']],
        #                columns=df.columns)

        total_fiyat = pd.DataFrame([['Total Fiyat', '', sum_fiyat, '', '', '', '', '', '']],
                         columns=df.columns)

        
        # Concatenate the total row to the original DataFrame
        df = pd.concat([df, total_row, total_fiyat])


        
        # Export DataFrame to Excel
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Search Results')
    
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Search Results']
    
        # Define a cell format for the blue table
        table_format = workbook.add_format({'bg_color': '#87CEEB'})

    
        # Apply the table format to the range of cells containing the total rows
        num_rows = df.shape[0]
        table_range = f"A{num_rows+1}:H{num_rows}"
        worksheet.conditional_format(table_range, {'type': 'no_errors', 'format': table_format})
    
        writer.close()
        output.seek(0)
    
        # Create a response with the Excel file
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=search_results.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response


    return render_template('search.html')

"""def update_order_complete_time(order_id):
    conn = get_users_db()
    cursor = conn.cursor()

    # Get the current datetime
    current_time = datetime.now()

    # Update the row with the order_complete_time
    cursor.execute("UPDATE orders SET order_complete_time = ? WHERE order_id = ?", (current_time, order_id))
    db.commit()

    # Close the database connection
    cursor.close()
    db.close()

@app.route('/update_order_complete_time', methods=['POST'])
def handle_update_order_complete_time():
    # Get the order_id from the request
    order_id = request.form.get('order_id')

    # Update the order complete time for the specified order_id
    update_order_complete_time(order_id)

    return 'Order complete time updated successfully.'"""

if __name__ == '__main__':
    app.run(port=50002)
