from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # session 用

# 管理員帳號密碼
ADMIN_USERNAME = "cyut"
ADMIN_PASSWORD = "001"

# 假資料範例
leave_records = [
    # {'user_id': 'guo0410', 'timestamp': '2025-10-20 14:00', 'start_date':'2025-10-21', 'end_date':'2025-10-22', 'leave_type':'事假', 'reason':'生病'}
]

# 管理員登入
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "帳號或密碼錯誤"
    return render_template("admin_login.html")

# 管理員總覽頁面
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("admin.html", records=leave_records)

# 登出
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# 你的其他請假表單與使用者頁面路由照原本設定
# @app.route("/") ...
# @app.route("/leave_form") ...
# @app.route("/records") ...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
