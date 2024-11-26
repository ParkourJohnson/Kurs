from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
    "student": {"password": "student123", "role": "student"},
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = users.get(username)
    if user and user["password"] == password:
        session["username"] = username
        session["role"] = user["role"]
        flash("Вы успешно вошли!", "success")
        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user["role"] == "staff":
            return redirect(url_for("staff_dashboard"))
        elif user["role"] == "student":
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
