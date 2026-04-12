from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)
app.debug = True  # 🔥 HATALARI GÖSTER

# 🔐 DB
def get_conn():
    print("ŞİFRE:", os.environ.get("DB_PASSWORD"))  # TEST

    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153",
        password=os.environ.get("DB_PASSWORD"),
        port=5432,
        sslmode="require"
    )

# 🔹 LOGIN
@app.route('/')
def login_page():
    return '''
    <style>
    body {font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;}
    .box {background:white;padding:30px;border-radius:10px;}
    input {display:block;margin:10px 0;padding:10px;width:200px;}
    button {padding:10px;background:#7ED957;border:none;width:100%;}
    </style>

    <form class="box" method="POST" action="/login">
        <h2>UMbellatum</h2>
        <input name="username" placeholder="Kullanıcı">
        <input type="password" name="password" placeholder="Şifre">
        <label><input type="checkbox" name="remember"> Beni hatırla</label>
        <button>Giriş Yap</button>
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    if request.form.get("username") == "admin" and request.form.get("password") == "1234":
        session["user"] = "admin"
        if request.form.get("remember"):
            session.permanent = True
        return redirect("/dashboard")
    return "Hatalı giriş"

# 🔹 LAYOUT
def layout(content, title="Dashboard"):
    return f'''
    <html>
    <head>
    <style>
    body {{margin:0;font-family:Arial;display:flex;}}

    .sidebar {{
        width:220px;
        background:#0f172a;
        color:white;
        height:100vh;
        padding:20px;
    }}

    .menu a {{
        display:block;
        color:white;
        padding:10px;
        text-decoration:none;
        border-radius:6px;
    }}

    .menu a:hover {{
        background:#1e293b;
    }}

    .main {{
        flex:1;
        background:#f5f6f7;
        padding:20px;
    }}

    .card {{
        background:white;
        padding:20px;
        border-radius:10px;
        margin-bottom:20px;
        box-shadow:0 5px 15px rgba(0,0,0,0.1);
    }}

    table {{
        width:100%;
        background:white;
    }}

    th, td {{
        padding:10px;
        border-bottom:1px solid #eee;
    }}
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h2>UMbellatum</h2>
        <div class="menu">
            <a href="/dashboard">Dashboard</a>
            <a href="/stoklar">Stoklar</a>
            <a href="/satislar">Satışlar</a>
            <a href="/musteriler">Müşteriler</a>
            <a href="/ik">İnsan Kaynakları</a>
            <a href="/nakit">Nakit Yönetimi</a>
            <a href="/logout">Çıkış</a>
        </div>
    </div>

    <div class="main">
        <h2>{title}</h2>
        {content}
    </div>

    </body>
    </html>
    '''

# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    try:
        if "user" not in session:
            return redirect("/")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT adet FROM stok")
        rows = cur.fetchall()
        toplam = sum([r[0] for r in rows]) if rows else 0

        return layout(f"<div class='card'><h3>Toplam Stok</h3><h1>{toplam}</h1></div>")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 STOK
@app.route('/stoklar')
def stoklar():
    try:
        if "user" not in session:
            return redirect("/")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT urun, adet, tarih FROM stok ORDER BY id DESC")
        rows = cur.fetchall()

        html = "<div class='card'><form method='POST' action='/ekle'>"
        html += "<input name='urun' placeholder='Ürün'>"
        html += "<input name='adet' type='number' placeholder='Adet'>"
        html += "<button>Kaydet</button></form></div>"

        html += "<table><tr><th>Ürün</th><th>Adet</th><th>Tarih</th></tr>"

        for r in rows:
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

        html += "</table>"

        return layout(html, "Stoklar")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 EKLE
@app.route('/ekle', methods=['POST'])
def ekle():
    try:
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
            (
                request.form.get("urun"),
                int(request.form.get("adet")),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/stoklar")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 DİĞER SAYFALAR
@app.route('/satislar')
def satislar():
    return layout("<div class='card'>Satışlar</div>", "Satışlar")

@app.route('/musteriler')
def musteriler():
    return layout("<div class='card'>Müşteriler</div>", "Müşteriler")

@app.route('/ik')
def ik():
    return layout("<div class='card'>İnsan Kaynakları</div>", "İK")

@app.route('/nakit')
def nakit():
    return layout("<div class='card'>Nakit Yönetimi</div>", "Nakit")

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
