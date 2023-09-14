from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

users = []  # List to store user data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    hali_sayisi = int(request.form['hali_sayisi'])
    phone_number = request.form['phone_number']

    user = {
        'username': username,
        'email': email,
        'hali_sayisi': hali_sayisi,
        'phone_number': phone_number
    }

    users.append(user)  # Add user to the list

    return jsonify({'message': 'User added successfully'})

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_results', methods=['POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        results = []
        for user in users:
            if (search_term.lower() in user['username'].lower() or
                    search_term.lower() in user['email'].lower() or
                    search_term.lower() in str(user['hali_sayisi']) or
                    search_term.lower() in user['phone_number']):
                results.append(user)
        return render_template('search_results.html', results=results)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(port=50001, debug=True)