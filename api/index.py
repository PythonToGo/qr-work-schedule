from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

# current/template directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, '../templates')

# .env load
load_dotenv(os.path.join(current_dir, '../.env'))

# initialize Flask 
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv('SECRET_KEY') 

# check env variables
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"LOGIN_PASSWORD: {os.getenv('LOGIN_PASSWORD')}")

# logging
logging.basicConfig(level=logging.INFO)

# db initialize
def init_db():
    try:
        db_path = os.path.join(current_dir, 'schedule.db')
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week INTEGER,
                day TEXT,
                status TEXT
            )''')
            conn.commit()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")

# dates generator
def generate_dates():
    today = datetime.today()
    start_this_week = today - timedelta(days=today.weekday())
    start_next_week = start_this_week + timedelta(days=7)

    this_week_dates = [(start_this_week + timedelta(days=i)).day for i in range(5)]
    next_week_dates = [(start_next_week + timedelta(days=i)).day for i in range(5)]

    return this_week_dates, next_week_dates

# index route
@app.route('/')
def index():
    try:
        db_path = os.path.join(current_dir, 'schedule.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT week, status FROM schedule ORDER BY week, id')
            data = cursor.fetchall()

        this_week_status = [row[1] for row in data if row[0] == 0]
        next_week_status = [row[1] for row in data if row[0] == 1]

        this_week_dates, next_week_dates = generate_dates()
        return render_template('index.html', this_week_status=this_week_status, next_week_status=next_week_status,
                               this_week_dates=this_week_dates, next_week_dates=next_week_dates)
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

# 비밀번호 입력 페이지 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        login_password = os.getenv('LOGIN_PASSWORD')
        if password == login_password:
            session['logged_in'] = True
            return redirect(url_for('update'))
        else:
            error = 'Invalid password'
            return render_template('login.html', error=error)
    return render_template('login.html')

# update route
@app.route('/update', methods=['GET', 'POST'])
def update():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    this_week_dates, next_week_dates = generate_dates()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    if request.method == 'POST':
        try:
            schedule = []
            for i, day in enumerate(days):
                schedule.append((0, day, request.form[f'this_week_{day}']))
                schedule.append((1, day, request.form[f'next_week_{day}']))

            db_path = os.path.join(current_dir, 'schedule.db')
            with sqlite3.connect(db_path) as conn:
                conn.execute('DELETE FROM schedule')
                conn.executemany('INSERT INTO schedule (week, day, status) VALUES (?, ?, ?)', schedule)
                conn.commit()
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Error in update route: {e}")
            return "Internal Server Error", 500
    return render_template('update.html', this_week_dates=this_week_dates, next_week_dates=next_week_dates, days=days, zip=zip)

# Vercel Serverless Function entry point
def handler(request, context):
    init_db()  # Initialize the database
    return app

# # internal server TEST
# if __name__ == '__main__':
#     init_db()
#     app.run(host='127.0.0.1', port=8000, debug=True)

# init_db() initialization
init_db()