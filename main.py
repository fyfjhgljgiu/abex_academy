import sqlite3

DB_NAME = "academy.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    group_name TEXT
)
""")

conn.commit()

print("✅ قاعدة بيانات الأكاديمية جاهزة")
print("📁 الملف: academy.db")

conn.close()

