from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "leave_records.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    leave_type TEXT,
                    reason TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# 首頁 - 綁定名字
@app.route("/", methods=["GET", "POST"])
def bind_name():
    if request.method == "POST":
        name = request.form.get("name").strip()
        if name:
            session["name"] = name
            return redirect(url_for("leave_form"))
    return render_template("bind_name.html")

# 請假表單
@app.route("/leave_form", methods=["GET", "POST"])
def leave_form():
    if "name" not in session:
        return redirect(url_for("bind_name"))

    leave_types = ["病假", "特休", "公假", "生理假", "事假", "補休", "婚假", "喪假", "產假", "陪產假"]

    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        leave_type = request.form.get("leave_type")
        reason = request.form.get("reason").strip()

        # 日期檢查
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if end_dt < start_dt:
                error = "結束日期不能早於開始日期"
                return render_template("leave_form.html", leave_types=leave_types, error=error)
        except:
            error = "日期格式錯誤"
            return render_template("leave_form.html", leave_types=leave_types, error=error)

        # 儲存到 SQLite
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO leaves (name, start_date, end_date, leave_type, reason) VALUES (?, ?, ?, ?, ?)",
                  (session["name"], start_date, end_date, leave_type, reason))
        conn.commit()
        conn.close()

        return redirect(url_for("my_records"))

    return render_template("leave_form.html", leave_types=leave_types)

# 我的請假紀錄
@app.route("/my_records")
def my_records():
    if "name" not in session:
        return redirect(url_for("bind_name"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, start_date, end_date, leave_type, reason FROM leaves WHERE name=?", (session["name"],))
    records = c.fetchall()
    conn.close()
    return render_template("records.html", records=records)

# 登出
@app.route("/logout")
def logout():
    session.pop("name", None)
    session.pop("admin_logged_in", None)
    return redirect(url_for("bind_name"))

# 管理員登入
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "cyut" and password == "001":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "帳號或密碼錯誤"
            return render_template("admin_login.html", error=error)
    return render_template("admin_login.html")

# 管理員看所有請假紀錄
@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, start_date, end_date, leave_type, reason FROM leaves")
    records = c.fetchall()
    conn.close()
    return render_template("admin.html", records=records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
