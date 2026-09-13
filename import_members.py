import sqlite3
import csv

DB_NAME = "academy.db"
CSV_FILE = "members.csv"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

with open(CSV_FILE, newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    added = 0
    skipped = 0

    for row in reader:
        name = row["name"].strip()
        phone = row["phone"].strip()
        group_name = row.get("group_name", "").strip()

        try:
            cursor.execute(
                """
                INSERT INTO members (name, phone, group_name)
                VALUES (?, ?, ?)
                """,
                (name, phone, group_name)
            )
            added += 1

        except sqlite3.IntegrityError:
            skipped += 1

conn.commit()
conn.close()

print(f"✅ تمت إضافة {added} عضو")
print(f"⚠️ تم تجاهل {skipped} رقم مكرر")

