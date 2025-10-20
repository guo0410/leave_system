from flask import Flask, render_template, request, redirect, session, url_for
import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Attr

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
table = dynamodb.Table('leave_records')  # 你的 DynamoDB Table 名稱

# 管理員帳號
ADMIN_USERNAME = "cyut"
ADMIN_PASSWORD = "001"

# 首頁 - 綁定名字
@app.route("/", methods=["GET", "POST"])
def bind_name():
    if request.method == "POST":
        user_name = request.form.get('user_name', '').strip()
        if not user_name:
            return render_template("bind_name.html", error="請輸入姓名")
        session['user_name'] = user_name
        session.pop('is_admin', None)
        return redirect(url_for("leave_form"))
    return render_template("bind_name.html")

# 請假表單
@app.route("/leave_form", methods=["GET", "POST"])
def leave_form():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    if request.method == "POST":
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        leave_type = request.form.get('leave_type')
        reason = request.form.get('reason')
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
        return redirect(url_for("records"))

    return render_template("leave_form.html", user_name=session['user_name'])

# 查看請假紀錄
@app.route("/records")
def records():
    if 'user_name' not in session and not session.get('is_admin'):
        return redirect(url_for("bind_name"))

    if session.get('is_admin'):
        response = table.scan()
        records = response.get('Items', [])
    else:
        response = table.scan(
            FilterExpression=Attr('user_name').eq(session['user_name'])
        )
        records = response.get('Items', [])

    records.sort(key=lambda x: x['start_date'])
    return render_template("records.html", records=records, is_admin=session.get('is_admin', False))

# 管理員登入
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            session['user_name'] = "管理員"
            return redirect(url_for("records"))
        else:
            return render_template("admin_login.html", error="帳號或密碼錯誤")
    return render_template("admin_login.html")

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("bind_name"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
