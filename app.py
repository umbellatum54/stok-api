from flask import Flask, request, redirect, session, send_from_directory
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "/tmp/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# DB
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153",
        password=os.environ.get("DB_PASSWORD"),
        port=5432,
        sslmode="require"
    )

# LOGIN
@app.route('/')
def login():
    return '''
    <form method="POST" action="/giris">
        <h2>UMbellatum</h2>
        <input name="u" placeholder="Kullanıcı">
        <button>Giriş</button>
    </form>
    '''

@app.route('/giris', methods=['POST'])
def giris():
    session["user"] = request.form.get("u")
    return redirect("/dashboard")

# LAYOUT (FULL MENÜ)
def layout(content, title="Panel"):
    return f'''
    <html>
    <head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
    body {{margin:0;font-family:Arial;display:flex;background:#f4f6f9;}}

    .sidebar {{
        width:250px;
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
    }}

    .menu a:hover {{background:#1e293b;}}

    .main {{flex:1;}}

    .top {{background:#3c8dbc;color:white;padding:15px;}}

    .content {{padding:20px;}}

    .card {{
        background:white;
        padding:20px;
        border-radius:10px;
        margin-bottom:20px;
    }}
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h2>UMbellatum</h2>

        <div class="menu">
            <a href="/dashboard"><i class="fa fa-home"></i> Dashboard</a>
            <a href="/stok"><i class="fa fa-box"></i> Depo - Stok</a>
            <a href="/sayim"><i class="fa fa-check"></i> Stok Sayım</a>
            <a href="#"><i class="fa fa-users"></i> İnsan Kaynakları</a>
            <a href="#"><i class="fa fa-wallet"></i> Nakit Yönetimi</a>
            <a href="#"><i class="fa fa-truck"></i> Tedarikçiler</a>
            <a href="#"><i class="fa fa-cog"></i> Ayarlar</a>
        </div>
    </div>

    <div class="main">
        <div class="top">{title}</div>
        <div class="content">{content}</div>
    </div>

    </body>
    </html>
    '''

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    return layout("<div class='card'>Dashboard hazır</div>", "Dashboard")

# STOK
@app.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT,
        gorsel TEXT
    )
    """)

    cur.execute("SELECT * FROM urunler")
    urunler = cur.fetchall()

    html = '''
    <div class="card">
    <h3>Ürün Kartı</h3>
    <form method="POST" action="/urun_ekle" enctype="multipart/form-data">
        <input name="ad" placeholder="Ürün">
        <input name="renk" placeholder="Renk">
        <input type="file" name="gorsel">
        <button>Kaydet</button>
    </form>
    </div>
    '''

    for u in urunler:
        img = ""
        if u[3]:
            img = f"<img src='/img/{u[3]}' width='80'>"

        html += f"<div class='card'>{img}<br>{u[1]} - {u[2]}</div>"

    return layout(html, "Depo - Stok")

# GÖRSEL SERVİS
@app.route('/img/<filename>')
def img(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ÜRÜN EKLE
@app.route('/urun_ekle', methods=['POST'])
def urun_ekle():
    file = request.files.get('gorsel')
    filename = ""

    if file and file.filename != "":
        filename = str(datetime.now().timestamp()).replace(".", "") + "_" + file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO urunler (ad,renk,gorsel) VALUES (%s,%s,%s)",
        (request.form['ad'], request.form['renk'], filename)
    )

    conn.commit()

    return redirect("/stok")

# SAYIM
@app.route('/sayim')
def sayim():
    return layout("<div class='card'>Sayım ekranı hazır</div>", "Stok Sayım")
