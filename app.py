from flask import Flask, request, redirect, session, send_from_directory, Response
import psycopg2
from datetime import datetime
import os
import csv

app = Flask(__name__)
app.secret_key = "secret123"

LOGO_PATH = "/tmp/logo.png"

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

# INIT
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS depo(id SERIAL PRIMARY KEY, ad TEXT)
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler(
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT,
        marka TEXT,
        kod TEXT,
        raf TEXT,
        depo TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hareket(
        id SERIAL PRIMARY KEY,
        urun TEXT,
        renk TEXT,
        depo TEXT,
        adet INT,
        tip TEXT,
        tarih TEXT,
        userx TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# LOGIN
@app.route('/')
def login():
    return '''
    <style>
    body{display:flex;justify-content:center;align-items:center;height:100vh;background:#eef2f7;font-family:Arial}
    .box{background:white;padding:30px;border-radius:10px;width:300px}
    input{width:100%;padding:10px;margin:10px 0}
    button{width:100%;padding:10px;background:#00a65a;color:white;border:none}
    </style>
    <form class="box" method="POST" action="/giris">
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
def layout(content, title):
    logo = "<h3>UMbellatum</h3>"
    if os.path.exists(LOGO_PATH):
        logo = "<img src='/logo' width='120'>"

    return f"""
    <html>
    <head>
    <style>
    body{{margin:0;font-family:Arial;display:flex;background:#f4f6f9}}
    .sidebar{{width:250px;background:#0f172a;color:white;height:100vh;padding:20px}}
    .menu a{{display:block;color:white;padding:10px;text-decoration:none}}
    .menu a:hover{{background:#1e293b}}
    .main{{flex:1}}
    .top{{background:#3c8dbc;color:white;padding:15px}}
    .content{{padding:20px}}
    .card{{background:white;padding:20px;margin-bottom:20px;border-radius:10px}}
    button{{padding:10px;margin:5px;border:none;color:white;cursor:pointer}}
    .green{{background:#00a65a}}
    .red{{background:#dd4b39}}
    .blue{{background:#3c8dbc}}
    .orange{{background:#f39c12}}
    .modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5)}}
    .modal-content{{background:white;margin:5% auto;padding:20px;width:80%}}
    </style>

    <script>
    function openM(id){{document.getElementById(id).style.display='block'}}
    function closeM(id){{document.getElementById(id).style.display='none'}}

    function addRow(){{
        let div=document.getElementById("rows")
        div.innerHTML+=div.children[0].outerHTML
    }}
    </script>
    </head>

    <body>

    <div class="sidebar">
    {logo}

    <div class="menu">
    <a href="/dashboard">Dashboard</a>

    <b>Online Pazaryeri</b>
    <a>Trendyol</a>
    <a>Hepsiburada</a>
    <a>Pazarama</a>
    <a>N11</a>
    <a>Amazon</a>
    <a>Web Sitem</a>

    <hr>

    <a href="/stok">Depo - Stok</a>
    <a href="/ayar">Ayarlar</a>
    </div>
    </div>

    <div class="main">
    <div class="top">{title}</div>
    <div class="content">{content}</div>
    </div>

    </body>
    </html>
    """

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM urunler")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM depo")
    d = cur.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM hareket WHERE tarih LIKE %s",(today+"%",))
    i = cur.fetchone()[0]

    html=f"""
    <div class='card'>Stok Kartı: {u}</div>
    <div class='card'>Depo: {d}</div>
    <div class='card'>Bugünkü İşlem: {i}</div>
    """

    return layout(html,"Dashboard")

# STOK
@app.route('/stok')
def stok():
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT ad FROM urunler")
    urun=[x[0] for x in cur.fetchall()]

    cur.execute("SELECT DISTINCT renk FROM urunler")
    renk=[x[0] for x in cur.fetchall()]

    html=f"""
    <div class='card'>
    <button class='green' onclick="openM('urun')">Ürün Kartı</button>
    <button class='blue' onclick="openM('giris')">Üretim Girişi</button>
    <button class='red' onclick="openM('cikis')">Stok Çıkış</button>
    <button class='orange' onclick="openM('ozet')">Stok Özeti</button>
    </div>

    <!-- ÜRÜN -->
    <div id='urun' class='modal'><div class='modal-content'>
    <form method='POST' action='/urun'>
    <input name='ad' placeholder='Ürün'>
    <input name='renk' placeholder='Renk'>
    <input name='marka'>
    <input name='kod'>
    <input name='raf'>
    <button>Kaydet</button>
    </form>
    <button onclick="closeM('urun')">Kapat</button>
    </div></div>

    <!-- GİRİŞ -->
    <div id='giris' class='modal'><div class='modal-content'>
    <form method='POST' action='/giris_ekle'>
    <div id='rows'>
    <div>
    <select name='urun'>{''.join([f"<option>{x}</option>" for x in urun])}</select>
    <select name='renk'>{''.join([f"<option>{x}</option>" for x in renk])}</select>
    <input name='adet'>
    </div>
    </div>
    <button type='button' onclick='addRow()'>+ Satır</button>
    <button>Kaydet</button>
    </form>
    <button onclick="closeM('giris')">Kapat</button>
    </div></div>

    <!-- ÇIKIŞ -->
    <div id='cikis' class='modal'><div class='modal-content'>
    <form method='POST' action='/cikis_ekle'>
    <select name='urun'>{''.join([f"<option>{x}</option>" for x in urun])}</select>
    <select name='renk'>{''.join([f"<option>{x}</option>" for x in renk])}</select>
    <input name='adet'>
    <button>Kaydet</button>
    </form>
    </div></div>
    """

    # LOG
    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs=cur.fetchall()

    html+="<div class='card'><table>"
    for l in logs:
        html+=f"<tr><td>{l[1]}</td><td>{l[2]}</td><td>{l[4]}</td><td>{l[5]}</td></tr>"
    html+="</table></div>"

    return layout(html,"Depo - Stok")

# EKLE
@app.route('/urun', methods=['POST'])
def urun():
    conn=get_conn(); cur=conn.cursor()
    cur.execute("INSERT INTO urunler(ad,renk,marka,kod,raf) VALUES(%s,%s,%s,%s,%s)",
                (request.form['ad'],request.form['renk'],request.form['marka'],request.form['kod'],request.form['raf']))
    conn.commit()
    return redirect("/stok")

@app.route('/giris_ekle', methods=['POST'])
def giris_ekle():
    conn=get_conn(); cur=conn.cursor()

    urun=request.form.getlist('urun')
    renk=request.form.getlist('renk')
    adet=request.form.getlist('adet')

    for i in range(len(urun)):
        cur.execute("INSERT INTO hareket(urun,renk,adet,tip,tarih,userx) VALUES(%s,%s,%s,'Giriş',%s,%s)",
                    (urun[i],renk[i],adet[i],datetime.now().strftime("%Y-%m-%d %H:%M"),session.get("user")))
    conn.commit()
    return redirect("/stok")

@app.route('/cikis_ekle', methods=['POST'])
def cikis_ekle():
    conn=get_conn(); cur=conn.cursor()
    cur.execute("INSERT INTO hareket(urun,renk,adet,tip,tarih,userx) VALUES(%s,%s,%s,'Çıkış',%s,%s)",
                (request.form['urun'],request.form['renk'],request.form['adet'],datetime.now().strftime("%Y-%m-%d %H:%M"),session.get("user")))
    conn.commit()
    return redirect("/stok")

# LOGO
@app.route('/ayar')
def ayar():
    return layout("""
    <form method='POST' action='/logo' enctype='multipart/form-data'>
    <input type='file' name='logo'>
    <button>Yükle</button>
    </form>
    ""","Ayarlar")

@app.route('/logo', methods=['POST'])
def logo():
    file=request.files['logo']
    file.save(LOGO_PATH)
    return redirect("/ayar")

@app.route('/logo')
def get_logo():
    return send_from_directory("/tmp","logo.png")
