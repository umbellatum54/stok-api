from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)

# 🔐 DB
def get_conn():
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
def login():
    return '''
    <style>
    body {font-family:Arial;background:#eef2f7;display:flex;justify-content:center;align-items:center;height:100vh;}
    .box {background:white;padding:30px;border-radius:10px;width:300px;}
    input {width:100%;padding:10px;margin:10px 0;}
    button {width:100%;padding:12px;background:#7ED957;border:none;}
    </style>

    <form class="box" method="POST" action="/giris">
        <h2>UMbellatum</h2>
        <input name="u" placeholder="Kullanıcı">
        <input type="password" name="p" placeholder="Şifre">
        <button>Giriş Yap</button>
    </form>
    '''

@app.route('/giris', methods=['POST'])
def giris():
    if request.form.get("u") == "admin":
        session["user"] = "ok"
        return redirect("/dashboard")
    return "Hatalı"

# 🔹 LAYOUT
def layout(content, title="Panel"):

    return f'''
    <html>
    <head>

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">

    <style>
    body {{
        margin:0;
        font-family:Arial;
        display:flex;
        background:#f4f6f9;
    }}

    .sidebar {{
        width:260px;
        background:#0f172a;
        color:white;
        height:100vh;
        padding:20px;
    }}

    .logo {{
        text-align:center;
        margin-bottom:30px;
    }}

    .logo img {{
        width:120px;
    }}

    .menu a {{
        display:block;
        color:white;
        padding:12px;
        text-decoration:none;
        border-radius:6px;
        margin-bottom:5px;
    }}

    .menu a:hover {{
        background:#1e293b;
    }}

    .submenu {{
        margin-left:15px;
        display:none;
    }}

    .submenu a {{
        font-size:14px;
        background:#1e293b;
    }}

    .main {{
        flex:1;
    }}

    .topbar {{
        background:#3c8dbc;
        color:white;
        padding:15px;
    }}

    .content {{
        padding:20px;
    }}

    .card {{
        background:white;
        padding:20px;
        border-radius:10px;
        margin-bottom:20px;
        box-shadow:0 5px 15px rgba(0,0,0,0.1);
    }}

    </style>

    <script>
    function toggleMenu(id){{
        var x = document.getElementById(id);
        if(x.style.display==="block") x.style.display="none";
        else x.style.display="block";
    }}
    </script>

    </head>

    <body>

    <div class="sidebar">

        <div class="logo">
            <img src="/static/logo.png">
        </div>

        <div class="menu">

            <a href="/dashboard"><i class="fa fa-home"></i> Dashboard</a>

            <a onclick="toggleMenu('pazar')">
                <i class="fa fa-store"></i> Online Pazaryeri
            </a>

            <div id="pazar" class="submenu">
                <a href="#">Trendyol</a>
                <a href="#">Hepsiburada</a>
                <a href="#">Pazarama</a>
                <a href="#">N11</a>
                <a href="#">Amazon</a>
                <a href="#">Web Sitem</a>
            </div>

            <a href="/stok"><i class="fa fa-box"></i> Depo - Stok</a>
            <a href="/ik"><i class="fa fa-users"></i> İnsan Kaynakları</a>
            <a href="#"><i class="fa fa-wallet"></i> Nakit Yönetimi</a>
            <a href="#"><i class="fa fa-truck"></i> Tedarikçiler</a>
            <a href="#"><i class="fa fa-cog"></i> Ayarlar</a>

        </div>

    </div>

    <div class="main">

        <div class="topbar">{title}</div>

        <div class="content">
            {content}
        </div>

    </div>

    </body>
    </html>
    '''

# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return layout("<div class='card'>Dashboard Hazır</div>", "Dashboard")

# 🔹 DEPO STOK (BAŞLIYORUZ)
@app.route('/stok')
def stok():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT urun, adet FROM stok ORDER BY id DESC")
        rows = cur.fetchall()

        html = '''
        <div class="card">
            <h3>Stok Giriş</h3>
            <form method="POST" action="/ekle">
                <input name="urun" placeholder="Ürün"><br><br>
                <input name="adet" type="number" placeholder="Adet"><br><br>
                <button>Kaydet</button>
            </form>
        </div>
        '''

        html += "<div class='card'><table><tr><th>Ürün</th><th>Adet</th></tr>"

        for r in rows:
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>"

        html += "</table></div>"

        return layout(html, "Depo - Stok")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 EKLE
@app.route('/ekle', methods=['POST'])
def ekle():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stok (
        id SERIAL PRIMARY KEY,
        urun TEXT,
        adet INTEGER
    )
    """)

    cur.execute(
        "INSERT INTO stok (urun, adet) VALUES (%s, %s)",
        (request.form.get("urun"), int(request.form.get("adet")))
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/stok")

# 🔹 İK
@app.route('/ik')
def ik():
    return layout("<div class='card'>İnsan Kaynakları</div>", "İK")
