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

# LAYOUT
def layout(content, title="Panel"):
    return f'''
    <html>
    <head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
    body {{margin:0;font-family:Arial;display:flex;background:#f4f6f9;}}
    .sidebar {{width:250px;background:#0f172a;color:white;height:100vh;padding:20px;}}
    .menu a {{display:block;color:white;padding:10px;text-decoration:none}}
    .menu a:hover {{background:#1e293b}}
    .main {{flex:1}}
    .top {{background:#3c8dbc;color:white;padding:15px}}
    .content {{padding:20px}}
    .card {{background:white;padding:20px;border-radius:10px;margin-bottom:20px}}
    input,select {{padding:8px;margin:5px}}
    button {{padding:10px;background:#00a65a;color:white;border:none}}
    table {{width:100%}}
    th,td {{padding:8px;border-bottom:1px solid #ddd}}
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

# STOK SAYFA
@app.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    # TABLOLAR
    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT,
        gorsel TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hareket (
        id SERIAL PRIMARY KEY,
        urun TEXT,
        renk TEXT,
        adet INTEGER,
        tip TEXT,
        tarih TEXT,
        kullanici TEXT
    )
    """)

    # ÜRÜNLER
    cur.execute("SELECT * FROM urunler")
    urunler = cur.fetchall()

    # DROPDOWN
    cur.execute("SELECT DISTINCT ad FROM urunler")
    urun_list = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT renk FROM urunler")
    renk_list = [r[0] for r in cur.fetchall()]

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

    <div class="card">
    <h3>Stok Giriş</h3>
    <form method="POST" action="/stok_giris">
    Ürün:<select name="urun">
    '''

    for u in urun_list:
        html += f"<option>{u}</option>"

    html += "</select> Renk:<select name='renk'>"

    for r in renk_list:
        html += f"<option>{r}</option>"

    html += '''
    </select>
    <input name="adet" type="number" placeholder="Adet">
    <button>Giriş</button>
    </form>
    </div>

    <div class="card">
    <h3>Stok Çıkış</h3>
    <form method="POST" action="/stok_cikis">
        <input name="urun" placeholder="Ürün">
        <input name="adet" type="number" placeholder="Adet">
        <button style="background:red">Çıkış</button>
    </form>
    </div>

    <div class="card">
    <h3>Ürünler</h3>
    '''

    for u in urunler:
        img = ""
        if u[3]:
            img = f"<img src='/img/{u[3]}' width='80'>"

        html += f"<div>{img} {u[1]} - {u[2]}</div>"

    html += "</div>"

    # LOG
    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs = cur.fetchall()

    html += "<div class='card'><h3>Son İşlemler</h3><table>"
    html += "<tr><th>Ürün</th><th>Renk</th><th>Adet</th><th>Tip</th><th>Tarih</th><th>Kullanıcı</th></tr>"

    for l in logs:
        html += f"<tr><td>{l[1]}</td><td>{l[2]}</td><td>{l[3]}</td><td>{l[4]}</td><td>{l[5]}</td><td>{l[6]}</td></tr>"

    html += "</table></div>"

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

# STOK GİRİŞ
@app.route('/stok_giris', methods=['POST'])
def stok_giris():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO hareket (urun,renk,adet,tip,tarih,kullanici)
    VALUES (%s,%s,%s,'Giriş',%s,%s)
    """, (
        request.form['urun'],
        request.form['renk'],
        request.form['adet'],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        session.get("user")
    ))

    conn.commit()
    return redirect("/stok")

# STOK ÇIKIŞ
@app.route('/stok_cikis', methods=['POST'])
def stok_cikis():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO hareket (urun,adet,tip,tarih,kullanici)
    VALUES (%s,%s,'Çıkış',%s,%s)
    """, (
        request.form['urun'],
        request.form['adet'],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        session.get("user")
    ))

    conn.commit()
    return redirect("/stok")

# SAYIM
@app.route('/sayim')
def sayim():
    return layout("<div class='card'>Sayım ekranı hazır</div>", "Stok Sayım")
