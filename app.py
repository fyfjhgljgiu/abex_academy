from flask import Flask, request, redirect, Response, render_template_string, session, url_for
import sqlite3
import csv
import io
import os
from functools import wraps

app = Flask(__name__)

DB_NAME = "academy.db"

# ضع هذه القيم في Environment Variables عند النشر:
# ADMIN_PASSWORD = كلمة مرور المسؤول
# SECRET_KEY = مفتاح سري عشوائي وطويل
app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>دخول المسؤول</title>
<style>
body { font-family: Arial, sans-serif; background:#f4f6f8; margin:0; padding:20px; }
.container { max-width:450px; margin:70px auto; }
form { background:white; padding:25px; border-radius:12px; box-shadow:0 2px 8px #ddd; }
h1 { text-align:center; }
input, button { width:100%; box-sizing:border-box; padding:12px; margin-top:10px; border-radius:7px; border:1px solid #ccc; }
button { cursor:pointer; background:#222; color:white; }
.error { color:#b00020; text-align:center; margin-top:12px; }
</style>
</head>
<body>
<div class="container">
<form method="POST">
<h1>🔐 دخول المسؤول</h1>
<input type="password" name="password" placeholder="كلمة مرور المسؤول" required autofocus>
<button type="submit">دخول</button>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
</form>
</div>
</body>
</html>
"""


HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>إدارة أعضاء الأكاديمية</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 1100px;
    margin: auto;
}
h1 { text-align: center; }
.topbar { text-align:center; margin-bottom:20px; }
.logout {
    display:inline-block;
    background:#b00020;
    color:white;
    padding:10px 15px;
    border-radius:7px;
    text-decoration:none;
}
.cards {
    display:flex;
    gap:15px;
    margin-bottom:20px;
}
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    flex:1;
    text-align:center;
    box-shadow:0 2px 8px #ddd;
}
form {
    background:white;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
}
input, button {
    padding:10px;
    margin:5px;
    border-radius:7px;
    border:1px solid #ccc;
}
button {
    cursor:pointer;
    background:#222;
    color:white;
}
table {
    width:100%;
    background:white;
    border-collapse:collapse;
}
th, td {
    padding:10px;
    border-bottom:1px solid #ddd;
    text-align:center;
}
th {
    background:#222;
    color:white;
}
a { text-decoration:none; }
</style>
</head>

<body>
<div class="container">

<h1>📚 إدارة أعضاء الأكاديمية</h1>

<div class="topbar">
    <a class="logout" href="/logout">تسجيل خروج</a>
</div>

<div class="cards">
    <div class="card">
        <h3>إجمالي الأعضاء</h3>
        <h2>{{ count }}</h2>
    </div>
</div>

<form method="GET">
    <input type="text" name="search"
           placeholder="ابحث بالاسم أو الرقم"
           value="{{ search }}">
    <button type="submit">🔎 بحث</button>
    <a href="/">
        <button type="button">عرض الكل</button>
    </a>
    <a href="/export">
        <button type="button">📥 تصدير CSV</button>
    </a>
</form>

<form method="POST" action="/add">
    <h3>➕ إضافة عضو</h3>

    <input type="text" name="name" placeholder="الاسم">

    <input type="text" name="phone" placeholder="رقم الهاتف" required>

    <input type="text" name="group_name"
           placeholder="اسم المجموعة" value="Academy">

    <button type="submit">إضافة</button>
</form>

<table>
<tr>
    <th>#</th>
    <th>الاسم</th>
    <th>رقم الهاتف</th>
    <th>المجموعة</th>
</tr>

{% for member in members %}
<tr>
    <td>{{ member["id"] }}</td>
    <td>{{ member["name"] }}</td>
    <td>{{ member["phone"] }}</td>
    <td>{{ member["group_name"] }}</td>
</tr>
{% endfor %}

</table>

</div>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not ADMIN_PASSWORD:
            return render_template_string(
                LOGIN_HTML,
                error="لم يتم ضبط ADMIN_PASSWORD في إعدادات الخادم."
            )

        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("index"))

        return render_template_string(LOGIN_HTML, error="كلمة المرور غير صحيحة.")

    return render_template_string(LOGIN_HTML, error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@admin_required
def index():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        members = conn.execute(
            """
            SELECT id, name, phone, group_name
            FROM members
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            """,
            (f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        members = conn.execute(
            """
            SELECT id, name, phone, group_name
            FROM members
            ORDER BY id DESC
            """
        ).fetchall()

    count = conn.execute(
        "SELECT COUNT(*) FROM members"
    ).fetchone()[0]

    conn.close()

    return render_template_string(
        HTML,
        members=members,
        count=count,
        search=search
    )


@app.route("/add", methods=["POST"])
@admin_required
def add_member():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    group_name = request.form.get("group_name", "Academy").strip()

    conn = get_db()

    try:
        conn.execute(
            """
            INSERT INTO members (name, phone, group_name)
            VALUES (?, ?, ?)
            """,
            (name, phone, group_name)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/")


@app.route("/export")
@admin_required
def export_csv():
    conn = get_db()

    members = conn.execute(
        """
        SELECT name, phone, group_name
        FROM members
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    output = io.StringIO()
    output.write("\ufeff")

    writer = csv.writer(output)
    writer.writerow(["name", "phone", "group_name"])

    for member in members:
        writer.writerow([
            member["name"],
            member["phone"],
            member["group_name"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=members.csv"
        }
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
