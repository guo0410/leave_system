from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 假別列表
leave_types = ["事假", "病假", "生理假", "特休", "公假", "喪假", "婚假", "其他"]

# SQLite 初始化
def init_db():
    conn = sqlite3.connect('leave_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaves
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  leave_type TEXT,
                  reason TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 首頁：綁定名字
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'name' not in session:
        return redirect(url_for('bind_name'))
    return render_template('leave_form.html', leave_types=leave_types)

@app.route('/bind_name', methods=['POST'])
def bind_name():
    name = request.form.get('name')
    if name:
        session['name'] = name
    return redirect(url_for('index'))

@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    name = session.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    leave_type = request.form.get('leave_type')
    reason = request.form.get('reason')
    if name and start_date and end_date and leave_type and reason:
        conn = sqlite3.connect('leave_records.db')
        c = conn.cursor()
        c.execute("INSERT INTO leaves (name, start_date, end_date, leave_type, reason) VALUES (?, ?, ?, ?, ?)",
                  (name, start_date, end_date, leave_type, reason))
        conn.commit()
        conn.close()
    return redirect(url_for('my_records'))

@app.route('/my_records')
def my_records():
    name = session.get('name')
    conn = sqlite3.connect('leave_records.db')
    c = conn.cursor()
    c.execute("SELECT start_date, end_date, leave_type, reason FROM leaves WHERE name=?", (name,))
    records = c.fetchall()
    conn.close()
    return render_template('records.html', records=records)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bind_name'))

# 管理員登入
ADMIN_USERNAME = 'cyut'
ADMIN_PASSWORD = '001'

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "帳號或密碼錯誤"
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('leave_records.db')
    c = conn.cursor()
    c.execute("SELECT name, start_date, end_date, leave_type, reason FROM leaves")
    records = c.fetchall()
    conn.close()
    return render_template('admin.html', records=records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
