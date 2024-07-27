from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM login WHERE username = ? AND password = ?', (username, password))
        lookup = cursor.fetchone()  
        connection.close()

        if lookup:
            create_time = datetime.now().strftime('%Y:%m:%d_%H:%M')
            session_id = str(uuid.uuid4())

            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO session (username, session_id, create_time) VALUES (?, ?, ?)',
                           (username, session_id, create_time))
            connection.commit()
            connection.close()
            
            cookie_response = make_response(render_template('welcome.html', username=username, session_id=session_id))
            cookie_response.set_cookie('session_id', session_id)
            return cookie_response
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO login (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        connection.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/welcome')
def welcome():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM session WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    connection.close()

    if session:
        return render_template('welcome.html', username=session[0])
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    username = request.form['username']

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM session WHERE username = ?', (username,))
    connection.commit()
    connection.close()

    cookie_response = make_response(render_template('login.html'))
    cookie_response.delete_cookie('session_id')
    return cookie_response

if __name__ == '__main__':
    app.run(debug=True)
