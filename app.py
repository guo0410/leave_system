from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 暫存資料
leave_records = []          # 所有請假紀錄
user_bind = {}              # {line_userId: 姓名}

# 假資料測試用 LIFF userId
TEST_LINE_USER = "U1234567890"

# 主頁，先綁定姓名或直接填表
@app.route('/')
def index():
    line_user_id = TEST_LINE_USER  # 這裡測試用，正式上線可用 LIFF SDK 抓取
    if line_user_id in user_bind:
        # 已綁定姓名 → 直接請假表單
        return render_template('leave_form.html', name=user_bind[line_user_id])
    else:
        # 未綁定姓名 → 顯示綁定頁面
        return render_template('bind_name.html', user_id=line_user_id)

# 綁定姓名
@app.route('/bind', methods=['POST'])
def bind_name():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    if user_id and name:
        user_bind[user_id] = name
    return redirect(url_for('index'))

# 送出請假表單
@app.route('/submit', methods=['POST'])
def submit():
    user_id = TEST_LINE_USER
    name = user_bind.get(user_id, "未綁定")
    leave_type = request.form.get('leave_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    reason = request.form.get('reason')

    leave_records.append({
        "user_id": user_id,
        "name": name,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason
    })
    return redirect(url_for('records'))

# 顯示所有請假紀錄（後台）
@app.route('/records')
def records():
    return render_template('records.html', records=leave_records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

