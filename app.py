import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

def get_user(username):
    conn = sqlite3.connect("imsit.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = get_user(username)
    if user and user[1] == password:
        session["username"] = username
        session["role"] = user[2]
        flash("Вы успешно вошли!", "success")
        if user[2] == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user[2] == "staff":
            return redirect(url_for("staff_dashboard"))
        elif user[2] == "student":
            return redirect(url_for("student_dashboard"))
    else:
        flash("Неверный логин или пароль.", "danger")
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("index"))

@app.route("/admin")
def admin_dashboard():
    if session.get("role") == "admin":
        return render_template("admin_dashboard.html")
    return redirect(url_for("index"))

@app.route("/staff")
def staff_dashboard():
    if session.get("role") == "staff":
        return render_template("staff_dashboard.html")
    return redirect(url_for("index"))

@app.route("/student")
def student_dashboard():
    if session.get("role") == "student":
        return render_template("student_dashboard.html")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
