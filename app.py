from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)

# 🔥 DB
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153",
        password="Deneme1234",
        port=5432,
        sslmode="require"
    )

# 🔹 LOGIN SAYFA
@app.route('/')
def login_page():
    return '''
    <html>
    <head>
    <style>
    body {
        font-family: Arial;
        background: linear-gradient(135deg,#f0f2f5,#e4efe9);
        display:flex;justify-content:center;align-items:center;height:100vh;
    }
    .box {
        width:360px;background:white;padding:30px;border-radius:15px;
        box-shadow:0 10px 30px rgba(0,0,0,0.1);text-align:center;
    }
    input {width:100%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #ddd;}
    button {width:100%;padding:12px;background:#7ED957;border:none;border-radius:8px;font-weight:bold;}
    </style>
    </head>
    <body>
    <form class="box" method="POST" action="/login">
        <h2>UMbellatum</h2>
        <input name="username" placeholder="Kullanıcı">
        <input type="password" name="password" placeholder="Şifre">
        <label><input type="checkbox" name="remember"> Beni hatırla</label>
        <button>Giriş Yap</button>
    </form>
    </body>
    </html>
    '''

# 🔹 LOGIN
@app.route('/login', methods=['POST'])
def login():
    if request.form.get("username") == "admin" and request.form.get("password") == "1234":
        session["user"] = "admin"
        if request.form.get("remember"):
            session.permanent = True
        return redirect("/panel")
    return "Hatalı giriş"

# 🔹 PANEL (MODERN)
@app.route('/panel')
def panel():
    if "user" not in session:
        return redirect("/")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT urun, adet, tarih FROM stok ORDER BY id DESC")
    rows = cur.fetchall()

    toplam = sum([r[1] for r in rows]) if rows else 0

    html_rows = ""
    for r in rows:
        html_rows += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    return f'''
    <html>
    <head>
    <style>
    body {{
        font-family: Arial;
        background:#f5f6f7;
        margin:0;
    }}

    .header {{
        background:#2c3e50;
        color:white;
        padding:15px;
        display:flex;
        justify-content:space-between;
    }}

    .container {{
        padding:20px;
    }}

    .cards {{
        display:flex;
        gap:20px;
        margin-bottom:20px;
    }}

    .card {{
        background:white;
        padding:20px;
        border-radius:10px;
        flex:1;
        box-shadow:0 5px 15px rgba(0,0,0,0.1);
    }}

    table {{
        width:100%;
        background:white;
        border-radius:10px;
        overflow:hidden;
    }}

    th, td {{
        padding:12px;
        border-bottom:1px solid #eee;
        text-align:left;
    }}

    form {{
        background:white;
        padding:15px;
        border-radius:10px;
        margin-bottom:20px;
    }}

    input {{
        padding:10px;
        margin:5px;
    }}

    button {{
        background:#7ED957;
        border:none;
        padding:10px 15px;
        border-radius:6px;
        font-weight:bold;
    }}
    </style>
    </head>

    <body>

    <div class="header">
        <div>Stok Paneli</div>
        <a href="/logout" style="color:white;">Çıkış</a>
    </div>

    <div class="container">

        <div class="cards">
            <div class="card">
                <h3>Toplam Stok</h3>
                <h2>{toplam}</h2>
            </div>
        </div>

        <form method="POST" action="/ekle">
            <input name="urun" placeholder="Ürün">
            <input name="adet" type="number" placeholder="Adet">
            <button>Kaydet</button>
        </form>

        <table>
            <tr>
                <th>Ürün</th>
                <th>Adet</th>
                <th>Tarih</th>
            </tr>
            {html_rows}
        </table>

    </div>

    </body>
    </html>
    '''

# 🔹 EKLE
@app.route('/ekle', methods=['POST'])
def ekle():
    if "user" not in session:
        return redirect("/")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stok (
            id SERIAL PRIMARY KEY,
            urun TEXT,
            adet INTEGER,
            tarih TEXT
        )
    """)

    cur.execute(
        "INSERT INTO stok (urun, adet, tarih) VALUES (%s, %s, %s)",
        (request.form.get("urun"), int(request.form.get("adet")), datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/panel")

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
