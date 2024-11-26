from database_functions import *
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

@app.route("/admin/users")
def manage_users():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    users = get_all_users()
    return render_template("admin_users.html", users=users)

@app.route("/admin/users/add", methods=["GET", "POST"])
def add_user_page():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if add_user(username, password, role):
            flash("Пользователь добавлен!", "success")
            return redirect(url_for("manage_users"))
        else:
            flash("Ошибка: пользователь с таким именем уже существует.", "danger")
    return render_template("add_user.html")

@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user_page(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    user = get_user_by_id(user_id)
    if not user:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for("manage_users"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        update_user(user_id, username, password, role)
        flash("Данные пользователя обновлены.", "success")
        return redirect(url_for("manage_users"))
    return render_template("edit_user.html", user=user)

@app.route("/admin/users/delete/<int:user_id>")
def delete_user_page(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    delete_user(user_id)
    flash("Пользователь удален.", "info")
    return redirect(url_for("manage_users"))

@app.route('/admin/application-types')
def application_types():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    types = get_application_types()
    return render_template('application_types.html', types=types)

@app.route('/admin/application-types/add', methods=['POST'])
def add_application_type():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    name = request.form['name']
    description = request.form.get('description', '')
    if not name:
        flash("Название типа заявления обязательно!", "error")
        return redirect(url_for('application_types'))

    if (add_type(name, description)):
        flash("Новый тип заявления добавлен!", "success")
        return redirect(url_for('application_types'))
    else:
        flash("Ошибка при добавлении типа")
        return redirect(url_for('application_types'))

@app.route('/admin/application-types/delete/<int:type_id>')
def delete_application_type(type_id):
    delete_type(type_id)
    flash("Тип заявления удален!", "success")
    return redirect(url_for('application_types'))

if __name__ == "__main__":
    app.run(debug=True)
