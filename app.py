from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)

# 🔐 DB BAĞLANTI
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153",
        password=os.environ.get("DB_PASSWORD"),
        port=5432,
        sslmode="require"
    )

# 🔹 LOGIN SAYFASI
@app.route('/')
def login_page():
    return '''
    <style>
    body {font-family:Arial;background:#eef2f7;display:flex;justify-content:center;align-items:center;height:100vh;}
    .box {background:white;padding:30px;border-radius:10px;width:300px;box-shadow:0 5px 20px rgba(0,0,0,0.1);}
    input {width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:6px;}
    button {width:100%;padding:12px;background:#7ED957;border:none;border-radius:6px;font-weight:bold;}
    </style>

    <form class="box" method="POST" action="/login">
        <h2>UMbellatum</h2>
        <input name="username" placeholder="Kullanıcı">
        <input type="password" name="password" placeholder="Şifre">
        <label><input type="checkbox" name="remember"> Beni hatırla</label>
        <button>Giriş Yap</button>
    </form>
    '''

# 🔹 LOGIN
@app.route('/login', methods=['POST'])
def login():
    if request.form.get("username") == "admin" and request.form.get("password") == "1234":
        session["user"] = "admin"
        if request.form.get("remember"):
            session.permanent = True
        return redirect("/dashboard")
    return "Hatalı giriş"

# 🔹 LAYOUT
def layout(content, title="Panel"):
    return f'''
    <html>
    <head>
    <style>
    body {{margin:0;font-family:Arial;display:flex;background:#f4f6f9;}}

    .sidebar {{
        width:220px;
        background:#1e293b;
        color:white;
        height:100vh;
        padding:20px;
    }}

    .sidebar h2 {{margin-bottom:20px;}}

    .menu a {{
        display:block;
        color:white;
        padding:10px;
        text-decoration:none;
        border-radius:6px;
    }}

    .menu a:hover {{
        background:#334155;
    }}

    .main {{
        flex:1;
    }}

    .topbar {{
        background:#3c8dbc;
        color:white;
        padding:15px;
        display:flex;
        justify-content:space-between;
    }}

    .content {{
        padding:20px;
    }}

    .btn {{
        padding:15px 20px;
        border-radius:6px;
        color:white;
        display:inline-block;
        margin:5px;
        text-decoration:none;
        font-weight:bold;
    }}

    .green {{background:#00a65a;}}
    .red {{background:#dd4b39;}}
    .purple {{background:#605ca8;}}
    .orange {{background:#f39c12;}}

    .card {{
        display:inline-block;
        width:30%;
        background:white;
        padding:20px;
        margin:10px;
        border-radius:8px;
        text-align:center;
        box-shadow:0 2px 10px rgba(0,0,0,0.1);
    }}

    table {{
        width:100%;
        background:white;
        margin-top:20px;
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

        <div class="topbar">
            <div><b>EBS Depo-Stok</b></div>
            <div>Hoşgeldin admin</div>
        </div>

        <div class="content">
            <h2>{title}</h2>
            {content}
        </div>

    </div>

    </body>
    </html>
    '''

# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect("/")

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM stok")
        stok_sayisi = cur.fetchone()[0]

        html = f'''
        <h3>Hızlı İşlemler</h3>

        <a href="/stoklar" class="btn green">Stok Giriş</a>
        <a href="/stoklar" class="btn red">Stok Çıkış</a>
        <a href="#" class="btn purple">Transfer</a>
        <a href="/stoklar" class="btn orange">Stok Listesi</a>

        <div>
            <div class="card">
                <h3>STOK SAYISI</h3>
                <h1>{stok_sayisi}</h1>
            </div>

            <div class="card">
                <h3>DEPO SAYISI</h3>
                <h1>1</h1>
            </div>

            <div class="card">
                <h3>BUGÜNKÜ İŞLEM</h3>
                <h1>0</h1>
            </div>
        </div>
        '''

        return layout(html, "Dashboard")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 STOK SAYFASI
@app.route('/stoklar')
def stoklar():
    if "user" not in session:
        return redirect("/")

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT urun, adet, tarih FROM stok ORDER BY id DESC")
        rows = cur.fetchall()

        html = '''
        <form method="POST" action="/ekle">
            <input name="urun" placeholder="Ürün">
            <input name="adet" type="number" placeholder="Adet">
            <button>Kaydet</button>
        </form>
        '''

        html += "<table><tr><th>Ürün</th><th>Adet</th><th>Tarih</th></tr>"

        for r in rows:
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

        html += "</table>"

        return layout(html, "Stoklar")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 VERİ EKLE
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
    return layout("Satışlar", "Satışlar")

@app.route('/musteriler')
def musteriler():
    return layout("Müşteriler", "Müşteriler")

@app.route('/ik')
def ik():
    return layout("İnsan Kaynakları", "İK")

@app.route('/nakit')
def nakit():
    return layout("Nakit Yönetimi", "Nakit")

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
