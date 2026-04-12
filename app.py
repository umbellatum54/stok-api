from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"

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
    <form method="POST" action="/giris">
        <h2>Giriş</h2>
        <input name="u" placeholder="Kullanıcı"><br>
        <button>Giriş</button>
    </form>
    '''

@app.route('/giris', methods=['POST'])
def giris():
    session["user"] = request.form.get("u")
    return redirect("/stok")

# 🔹 LAYOUT
def layout(content, title="Panel"):
    return f'''
    <html>
    <head>
    <style>
    body{{margin:0;font-family:Arial;display:flex;background:#f4f6f9;}}
    .sidebar{{width:250px;background:#111;color:white;padding:20px;height:100vh;}}
    .sidebar a{{display:block;color:white;padding:10px;text-decoration:none}}
    .main{{flex:1}}
    .top{{background:#3c8dbc;color:white;padding:15px}}
    .content{{padding:20px}}
    .card{{background:white;padding:20px;border-radius:10px;margin-bottom:20px}}
    input,select{{padding:8px;margin:5px}}
    button{{padding:10px;background:#00a65a;color:white;border:none}}
    table{{width:100%}}
    th,td{{padding:8px;border-bottom:1px solid #ddd}}
    img{{width:60px}}
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h3>UMbellatum</h3>
        <a href="/stok">Depo-Stok</a>
        <a href="/sayim">Stok Sayım</a>
    </div>

    <div class="main">
        <div class="top">{title}</div>
        <div class="content">{content}</div>
    </div>

    </body>
    </html>
    '''

# 🔹 DB TABLO
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT,
        stok_kodu TEXT,
        kategori TEXT,
        marka TEXT,
        raf TEXT,
        gorsel TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hareket (
        id SERIAL PRIMARY KEY,
        urun TEXT,
        adet INTEGER,
        tip TEXT,
        tarih TEXT,
        kullanici TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# 🔹 STOK SAYFA
@app.route('/stok')
def stok():
    init_db()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM urunler")
    urunler = cur.fetchall()

    html = '''
    <div class="card">
    <h3>Ürün Kartı</h3>
    <form method="POST" action="/urun_ekle" enctype="multipart/form-data">
        <input name="ad" placeholder="Ürün adı">
        <input name="renk" placeholder="Renk">
        <input name="stok_kodu" placeholder="Stok kodu">
        <input name="kategori" placeholder="Kategori">
        <input name="marka" placeholder="Marka">
        <input name="raf" placeholder="Raf">
        <input type="file" name="gorsel">
        <button>Kaydet</button>
    </form>
    </div>
    '''

    html += "<div class='card'><h3>Ürünler</h3><table><tr><th>Resim</th><th>Ürün</th><th>Renk</th></tr>"

    for u in urunler:
        img = f"<img src='/static/uploads/{u[7]}'>" if u[7] else ""
        html += f"<tr><td>{img}</td><td>{u[1]}</td><td>{u[2]}</td></tr>"

    html += "</table></div>"

    return layout(html, "Depo-Stok")

# 🔹 ÜRÜN EKLE (GÖRSELLİ)
@app.route('/urun_ekle', methods=['POST'])
def urun_ekle():
    file = request.files['gorsel']
    filename = ""

    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO urunler (ad,renk,stok_kodu,kategori,marka,raf,gorsel)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form['ad'],
        request.form['renk'],
        request.form['stok_kodu'],
        request.form['kategori'],
        request.form['marka'],
        request.form['raf'],
        filename
    ))

    conn.commit()
    return redirect("/stok")

# 🔹 STOK SAYIM
@app.route('/sayim')
def sayim():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT ad FROM urunler")
    urunler = [r[0] for r in cur.fetchall()]

    html = '''
    <div class="card">
    <h3>Stok Sayım</h3>
    <form method="POST" action="/sayim_kaydet">
    Ürün: <select name="urun">
    '''

    for u in urunler:
        html += f"<option>{u}</option>"

    html += '''
    </select>
    Sayılan Adet: <input name="adet">
    <button>Kaydet</button>
    </form>
    </div>
    '''

    return layout(html, "Stok Sayım")

# 🔹 SAYIM KAYDET
@app.route('/sayim_kaydet', methods=['POST'])
def sayim_kaydet():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO hareket (urun,adet,tip,tarih,kullanici)
    VALUES (%s,%s,'Sayım',%s,%s)
    """, (
        request.form['urun'],
        request.form['adet'],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        session.get("user")
    ))

    conn.commit()
    return redirect("/sayim")
