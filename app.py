from flask import Flask, render_template, request, redirect, session, url_for
import boto3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# AWS DynamoDB 設定
AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
table = dynamodb.Table('leave_records_new')  # 改成你的新 Table 名稱

# 管理員帳號
ADMIN_USERNAME = "cyut"
ADMIN_PASSWORD = "001"

# 首頁 - 綁定名字
@app.route("/", methods=["GET", "POST"])
def bind_name():
    if request.method == "POST":
        session['user_name'] = request.form['user_name']
        return redirect(url_for("leave_form"))
    return render_template("bind_name.html")

# 請假表單
@app.route("/leave_form", methods=["GET"])
def leave_form():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    leave_types = [
        {"name": "事假", "color": "#fce4ec"},
        {"name": "病假", "color": "#e3f2fd"},
        {"name": "公假", "color": "#e8f5e9"},
        {"name": "喪假", "color": "#fff3e0"},
        {"name": "婚假", "color": "#f3e5f5"},
        {"name": "產假", "color": "#ede7f6"},
        {"name": "陪產假", "color": "#f9fbe7"},
        {"name": "生理假", "color": "#fffde7"},
        {"name": "特休假", "color": "#e0f7fa"}
    ]

    # 取得使用者自己的紀錄
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_name').eq(session['user_name'])
    )
    records = response.get('Items', [])
    records.sort(key=lambda x: x['start_date'])

    return render_template("leave_form.html", user_name=session['user_name'], leave_types=leave_types, records=records)

# 提交請假
@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    try:
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        leave_type = request.form['leave_type']
        reason = request.form['reason']
        user_name = session['user_name']

        # 儲存到 DynamoDB
        table.put_item(Item={
            'user_name': user_name,
            'start_date': start_date,
            'end_date': end_date,
            'leave_type': leave_type,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })

        return render_template("leave_success.html", user_name=user_name)

    except Exception as e:
        return f"<h3>送出失敗: {e}</h3><a href='{url_for('leave_form')}'>回表單</a>"

# 查看請假紀錄
@app.route("/records")
def records():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    if session.get('is_admin'):
        response = table.scan()
        records = response.get('Items', [])
    else:
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('user_name').eq(session['user_name'])
        )
        records = response.get('Items', [])

    records.sort(key=lambda x: x['start_date'])
    return render_template("records.html", records=records)

# 管理員登入
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for("records"))
        else:
            return "<h3>帳號或密碼錯誤</h3><a href='/admin_login'>返回</a>"
    return render_template("admin_login.html")

# 管理員登出
@app.route("/admin_logout")
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for("bind_name"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
