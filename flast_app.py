from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '123'  

# initialize DB
def init_db():
    with sqlite3.connect('schedule.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER,
            day TEXT,
            status TEXT
        )''')
        conn.commit()

# Day create
def generate_dates():
    today = datetime.today()
    start_this_week = today - timedelta(days=today.weekday())
    start_next_week = start_this_week + timedelta(days=7)

    this_week_dates = [(start_this_week + timedelta(days=i)).day for i in range(5)]
    next_week_dates = [(start_next_week + timedelta(days=i)).day for i in range(5)]

    return this_week_dates, next_week_dates

# homw route
@app.route('/')
def index():
    with sqlite3.connect('schedule.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT week, status FROM schedule ORDER BY week, id')
        data = cursor.fetchall()

    this_week_status = [row[1] for row in data if row[0] == 0]
    next_week_status = [row[1] for row in data if row[0] == 1]

    this_week_dates, next_week_dates = generate_dates()
    return render_template('index.html', this_week_status=this_week_status, next_week_status=next_week_status,
                           this_week_dates=this_week_dates, next_week_dates=next_week_dates)

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '123':  
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
        schedule = []
        for i, day in enumerate(days):
            schedule.append((0, day, request.form[f'this_week_{day}']))
            schedule.append((1, day, request.form[f'next_week_{day}']))

        with sqlite3.connect('schedule.db') as conn:
            conn.execute('DELETE FROM schedule')
            conn.executemany('INSERT INTO schedule (week, day, status) VALUES (?, ?, ?)', schedule)
            conn.commit()
        return redirect(url_for('index'))
    return render_template('update.html', this_week_dates=this_week_dates, next_week_dates=next_week_dates, days=days, zip=zip)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
