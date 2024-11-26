import sqlite3

# Установите соединение с базой данных
# Укажите путь к файлу базы данных, если он находится в текущей директории, либо полный путь
conn = sqlite3.connect("imsit.db")

# Создайте курсор для выполнения SQL-запросов
cursor = conn.cursor()

# Выполните SQL-запрос для выбора всех строк из таблицы
cursor.execute("SELECT * FROM users")

# Получите все строки из результата запроса
rows = cursor.fetchall()

# Выведите строки
for row in rows:
    print(row)

# Закройте соединение
conn.close()
