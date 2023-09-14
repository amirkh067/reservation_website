from flask import Flask, render_template, request, jsonify
from datetime import date
import sqlite3
import threading
from werkzeug.local import Local
import pandas as pd
from flask import make_response
from io import BytesIO
import json
import logging
from login import login_app




app = Flask(__name__)



# Create a thread-local storage for the database connection
connection_local = Local()

# Function to get the thread-local connection
def get_db():
    if not hasattr(connection_local, 'connection'):
        connection_local.connection = sqlite3.connect('users.db')
    return connection_local.connection

# Create the user table if it doesn't exist
def create_user_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            date_added TEXT,
            hali_sayisi INTEGER,
            phone_number TEXT
        )
    ''')
    conn.commit()

# Create the user table on application startup
create_user_table()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    hali_sayisi = int(request.form['hali_sayisi'])
    phone_number = request.form['phone_number']
    today = date.today().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    # Insert the user data into the database
    cursor.execute('''
        INSERT INTO users (username, email, date_added, hali_sayisi, phone_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, email, today, hali_sayisi, phone_number))
    conn.commit()

    # Return a JSON response indicating success
    return jsonify({'message': 'User added successfully!'})

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Query the database to retrieve matching users
        cursor.execute('''
            SELECT * FROM users
            WHERE LOWER(username) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR
                  LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?)
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        print(results)  # Debugging statement

        return render_template('search_results.html', results=results)


    return render_template('search.html')




# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


@app.route('/download_excel', methods=['POST'])
def download_excel():
    if request.method == 'POST':
        search_term = request.form['search_term']
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Query the database to retrieve matching users
        cursor.execute('''
            SELECT * FROM users
            WHERE LOWER(username) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR
                  LOWER(hali_sayisi) LIKE LOWER(?) OR LOWER(phone_number) LIKE LOWER(?)
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()

        # Convert results to a pandas DataFrame
        df = pd.DataFrame(results)

        # Export DataFrame to Excel
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Search Results')
        writer.close()
        output.seek(0)

        # Create a response with the Excel file
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=search_results.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response

    return render_template('search.html')





if __name__ == '__main__':
    app.run(port=50001)
