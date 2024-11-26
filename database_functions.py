import sqlite3

DB_PATH = "imsit.db"

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def get_all_users():
    """Получить список всех пользователей."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    """Получить данные пользователя по ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user(user_id, username, password, role):
    """Обновить данные пользователя."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET username = ?, password = ?, role = ?
        WHERE id = ?
    """, (username, password, role, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Удалить пользователя и сбросить автоинкремент."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Удаляем пользователя
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    # Сбрасываем автоинкремент
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
    conn.commit()
    conn.close()

def get_application_types():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM application_types")
    types = cursor.fetchall()
    conn.close()
    return types

def add_type(name, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO application_types (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def delete_type(type_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM application_types WHERE id = ?", (type_id,))
    conn.commit()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'application_types'")
    conn.commit()
    conn.close()