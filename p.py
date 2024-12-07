import sqlite3

query = """
ALTER TABLE email_verification_codes
ADD COLUMN email TEXT;
"""

conn = sqlite3.connect("imsit.db")

cursor = conn.cursor()

cursor.execute(query)

conn.commit()

conn.close()
