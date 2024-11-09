from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)

# 로그인 폼을 표시하는 홈 페이지 라우트
@app.route('/')
def index():
    return render_template('login.html')

# 로그인 기능을 처리하는 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 폼에서 사용자 이름과 비밀번호를 가져옴
        username = request.form['username']
        password = request.form['password']
        
        # 데이터베이스에 연결하고 사용자 확인
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM login WHERE username = ? AND password = ?', (username, password))
        lookup = cursor.fetchone()  
        connection.close()

        if lookup:
            # 자격 증명이 유효하면 세션을 생성
            create_time = datetime.now().strftime('%Y:%m:%d_%H:%M')
            session_id = str(uuid.uuid4())

            # 세션 정보를 데이터베이스에 삽입
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO session (username, session_id, create_time) VALUES (?, ?, ?)',
                           (username, session_id, create_time))
            connection.commit()
            connection.close()
            
            # 세션 ID를 쿠키에 설정하고 로그인 확인 페이지를 렌더링
            cookie_response = make_response(render_template('welcome.html', username=username, session_id=session_id))
            cookie_response.set_cookie('session_id', session_id)
            return cookie_response
        else:
            # 사용자가 유효하지 않으면 로그인 페이지로 리디렉션
            return redirect(url_for('login'))
    return render_template('login.html')

# 사용자 등록을 처리하는 라우트
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼에서 사용자 이름과 비밀번호를 가져옴
        username = request.form['username']
        password = request.form['password']

        # 새 사용자를 데이터베이스에 삽입
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO login (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        connection.close()

        # 성공적으로 등록한 후 로그인 페이지로 리디렉션
        return redirect(url_for('login'))
    return render_template('register.html')

# 세션이 필요한 로그인 확인 페이지 라우트
@app.route('/welcome')
def welcome():
    # 쿠키에서 세션 ID를 가져옴
    session_id = request.cookies.get('session_id')
    if not session_id:
        # 세션 ID가 없으면 로그인 페이지로 리디렉션
        return redirect(url_for('login'))

    # 데이터베이스에서 세션 ID를 확인함
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM session WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    connection.close()

    if session:
        # 세션이 유효하면 로그인 확인 페이지를 렌더링함
        return render_template('welcome.html', username=session[0])
    else:
        # 세션이 유효하지 않으면 로그인 페이지로 리디렉션함
        return redirect(url_for('login'))

# 사용자 로그아웃을 처리하는 라우트
@app.route('/logout', methods=['POST'])
def logout():
    # 폼에서 사용자 이름을 가져옴
    username = request.form['username']

    # 데이터베이스에서 세션을 삭제
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM session WHERE username = ?', (username,))
    connection.commit()
    connection.close()

    # 세션 쿠키를 삭제하고 로그인 페이지를 렌더링
    cookie_response = make_response(render_template('login.html'))
    cookie_response.delete_cookie('session_id')
    return cookie_response
#123
# Flask 애플리케이션을 실행
if __name__ == '__main__':
    app.run(debug=True)
