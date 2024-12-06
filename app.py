import os
from flask import send_from_directory
from database_functions import *
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = get_user(username)
    if user and user[2] == password:
        session["username"] = username
        session["role"] = user[3]
        flash("Вы успешно вошли!", "success")
        if user[3] == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user[3] == "staff":
            return redirect(url_for("staff_dashboard"))
        elif user[3] == "student":
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
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    delete_type(type_id)
    flash("Тип заявления удален!", "success")
    return redirect(url_for('application_types'))

@app.route('/student/apply')
def apply_form():
    if  session.get('role') != 'student':
        flash('Доступ запрещен!')
        return redirect(url_for('index'))

    application_types = get_application_types()

    return render_template('apply.html', application_types=application_types)

@app.route('/student/apply/submit', methods=['POST'])
def apply_submit():
    if session.get('role') != 'student':
        flash('Доступ запрещен!')
        return redirect(url_for('index'))

    student_id = get_user(session['username'])[0]
    type_id = request.form.get('type_id')
    comments = request.form.get('comments')
    file = request.files['file']

    file_path = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        create_application(student_id, type_id, comments, filename)
    else:
        create_application(student_id, type_id, comments, None)

    flash('Заявление успешно подано!', "success")
    return redirect(url_for('apply_form'))

@app.route('/student/my_applications')
def my_applications():
    if session.get('role') != 'student':
        flash('Доступ запрещен!')
        return redirect(url_for('index'))

    student_id = get_user(session['username'])[0]
    
    applications = get_applications_by_id(student_id)

    return render_template('my_applications.html', applications=applications)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if not session.get('role'):
        return redirect(url_for('index'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/staff/applications', methods=['GET', 'POST'])
def staff_applications():
    if session.get('role') != 'staff':
        flash('Доступ запрещен!')
        return redirect(url_for('index'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == 'POST':
        application_id = request.form.get('application_id')
        new_status = request.form.get('status')
        comment = request.form.get('comment')
        file = request.files.get('file')

        if application_id:
            if new_status:
                cursor.execute(
                    "UPDATE applications SET status = ? WHERE id = ?", 
                    (new_status, application_id)
                )
            if comment:
                cursor.execute(
                    "UPDATE applications SET comments = ? WHERE id = ?", 
                    (comment, application_id)
                )
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join('uploads', filename)
                file.save(filepath)
                cursor.execute(
                    "UPDATE applications SET file_path = ? WHERE id = ?", 
                    (filename, application_id)
                )
            conn.commit()
            flash('Изменения успешно сохранены', 'success')

        return redirect(url_for('staff_applications'))

    cursor.execute("""
        SELECT 
            a.id, 
            u.username AS student_name, 
            t.name AS type_name, 
            a.status, 
            a.comments, 
            a.file_path, 
            a.created_at
        FROM 
            applications a
        JOIN 
            users u ON a.student_id = u.id
        JOIN 
            application_types t ON a.type_id = t.id
        ORDER BY 
            a.created_at DESC
    """)
    applications = cursor.fetchall()

    conn.close()

    return render_template('staff_applications.html', applications=applications)

@app.route('/student/add_email', methods=['GET', 'POST'])
def add_email():
    if request.method == 'POST':
        if session['role'] != 'student':
            flash('Доступ запрещен')
            return redirect('/login')

        email = request.form['email']
        user_id = get_user(session['username'])[0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        conn.commit()
        conn.close()

        flash('Email успешно сохранён!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('add_email.html')

if __name__ == "__main__":
    app.run(debug=True)
