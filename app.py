from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # session 用

# 假別列表
leave_types = ["病假", "事假", "特休", "公假", "生理假", "婚假", "喪假", "產假", "陪產假", "公務假"]

# 簡單暫存資料，之後改用資料庫
leave_records = []

# 管理員帳號
ADMIN_USERNAME = "cyut"
ADMIN_PASSWORD = "001"

# ---------------- 使用者路由 ----------------
@app.route('/')
def index():
    # 首次使用者綁定姓名
    if 'name' not in session:
        return render_template('bind_name.html')
    return render_template('leave_form.html', leave_types=leave_types)

@app.route('/bind_name', methods=['POST'])
def bind_name():
    name = request.form.get('name')
    if name:
        session['name'] = name
    return redirect(url_for('index'))

@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    leave_type = request.form.get('leave_type')
    reason = request.form.get('reason')
    name = session.get('name', '未知使用者')

    # 簡單日期檢查
    if start_date > end_date:
        return "錯誤：開始日期不能晚於結束日期"

    leave_records.append({
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "leave_type": leave_type,
        "reason": reason
    })

    return redirect(url_for('index'))

@app.route('/my_records')
def my_records():
    name = session.get('name', '')
    my_records = [r for r in leave_records if r['name'] == name]
    return render_template('records.html', records=my_records)

# ---------------- 管理員路由 ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "帳號或密碼錯誤"
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html', records=leave_records)

# ---------------- 登出 ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------- 啟動 ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
