import sqlite3
import re

DB_NAME = "academy.db"

print("الصق الأرقام كلها هنا، وبعدها اضغط Enter ثم Ctrl+D")
raw = input() + "\n"

while True:
    try:
        raw += input() + "\n"
    except EOFError:
        break

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

added = 0
duplicates = 0
invalid = 0

for line in raw.splitlines():
    line = line.strip()

    if not line:
        continue

    # إزالة المسافات والشرطات والأقواس
    phone = re.sub(r"[^\d+]", "", line)

    # لازم يبدأ بـ +
    if not phone.startswith("+") or len(phone) < 8:
        invalid += 1
        continue

    try:
        cursor.execute(
            """
            INSERT INTO members (name, phone, group_name)
            VALUES (?, ?, ?)
            """,
            ("", phone, "Academy")
        )
        added += 1

    except sqlite3.IntegrityError:
        duplicates += 1

conn.commit()
conn.close()

print()
print("✅ تمت الإضافة:", added)
print("⚠️ أرقام مكررة:", duplicates)
print("❌ أرقام غير صالحة:", invalid)
print("💾 تم الحفظ داخل academy.db")

