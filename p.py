import sqlite3

conn = sqlite3.connect("imsit.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM applications")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
