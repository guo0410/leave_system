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
table = dynamodb.Table('leave_records')  # 你的 DynamoDB Table 名稱

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
@app.route("/leave_form", methods=["GET", "POST"])
def leave_form():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    return render_template("leave_form.html", user_name=session['user_name'])

# 提交請假
@app.route("/submit_leave", methods=["POST"])
def submit_leave():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

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

    return redirect(url_for("records"))

# 查看請假紀錄
@app.route("/records")
def records():
    if 'user_name' not in session:
        return redirect(url_for("bind_name"))

    if session.get('is_admin'):
        # 管理員看到所有紀錄
        response = table.scan()
        records = response.get('Items', [])
    else:
        # 一般使用者只看自己的
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('user_name').eq(session['user_name'])
        )
        records = response.get('Items', [])

    # 依日期排序
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
