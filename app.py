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
    .modal-content input{
    width:18%;
    padding:10px;
    margin:5px;
    border:1px solid #ccc;
    border-radius:6px;
}

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

    # KART SAYILARI
    cur.execute("SELECT COUNT(*) FROM urunler")
    stok_sayisi = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM depo")
    depo_sayisi = cur.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM hareket WHERE tarih LIKE %s", (today+"%",))
    islem_sayisi = cur.fetchone()[0]

    # LOG
    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs = cur.fetchall()

    # DROPDOWN
    cur.execute("SELECT DISTINCT ad FROM urunler")
    urunler = [x[0] for x in cur.fetchall()]

    cur.execute("SELECT DISTINCT renk FROM urunler")
    renkler = [x[0] for x in cur.fetchall()]

    cur.close()
    conn.close()

    html = f"""

    <div style="background:#f4f6f9;padding:20px">

    <!-- HIZLI İŞLEMLER -->
    <div style="background:white;padding:20px;border-radius:10px;margin-bottom:20px">

    <button class="green" onclick="openM('urun')">📦 Ürün Kartı</button>
    <button class="green" onclick="openM('giris')">⬇️ Stok Giriş</button>
    <button class="red" onclick="openM('cikis')">⬆️ Stok Çıkış</button>

    </div>

    <!-- KARTLAR -->
    <div style="display:flex;gap:20px;margin-bottom:20px">

    <div style="flex:1;background:white;padding:20px;border-radius:10px;display:flex;align-items:center">
    <div style="background:#00c0ef;width:80px;height:80px;border-radius:10px"></div>
    <div style="margin-left:20px">
    <h4>STOK KART SAYISI</h4>
    <h2>{stok_sayisi}</h2>
    </div>
    </div>

    <div style="flex:1;background:white;padding:20px;border-radius:10px;display:flex;align-items:center">
    <div style="background:#dd4b39;width:80px;height:80px;border-radius:10px"></div>
    <div style="margin-left:20px">
    <h4>DEPO SAYISI</h4>
    <h2>{depo_sayisi}</h2>
    </div>
    </div>

    <div style="flex:1;background:white;padding:20px;border-radius:10px;display:flex;align-items:center">
    <div style="background:#00a65a;width:80px;height:80px;border-radius:10px"></div>
    <div style="margin-left:20px">
    <h4>BUGÜNKÜ İŞLEM</h4>
    <h2>{islem_sayisi}</h2>
    </div>
    </div>

    </div>

    <!-- SON GİRİŞ -->
    <div style="background:white;padding:20px;border-radius:10px">

    <h2>Son Giriş Kaydı</h2>

    <table style="width:100%;margin-top:20px">

    <tr style="color:#666">
    <th>Tarih</th>
    <th>Ürün</th>
    <th>Renk</th>
    <th>Adet</th>
    <th>İşlem</th>
    <th>Kullanıcı</th>
    </tr>

    {''.join(f"""
    <tr>
    <td>{l[6]}</td>
    <td>{l[1]}</td>
    <td>{l[2]}</td>
    <td>{l[4]}</td>
    <td>{l[5]}</td>
    <td>{l[7]}</td>
    </tr>
    """ for l in logs)}

    </table>

    </div>

    </div>

    <!-- ÜRÜN MODAL -->
    <div id='urun' class='modal'>
    <div class='modal-content'>
    <h2>📦 Ürün Kartı</h2>

    <form method='POST' action='/urun'>
    <input name='ad' placeholder='Ürün'>
    <input name='renk' placeholder='Renk'>
    <input name='marka'>
    <input name='kod'>
    <input name='raf'>
    <button class='green'>Kaydet</button>
    </form>

    <button onclick="closeM('urun')">Kapat</button>
    </div>
    </div>

    <!-- GİRİŞ MODAL -->
    <div id='giris' class='modal'>
    <div class='modal-content'>
    <h2>⬇️ Stok Giriş</h2>

    <form method='POST' action='/giris_ekle'>

    <div id="rows">
    <div>
    <select name='urun'>{''.join([f"<option>{x}</option>" for x in urunler])}</select>
    <select name='renk'>{''.join([f"<option>{x}</option>" for x in renkler])}</select>
    <input name='adet'>
    </div>
    </div>

    <button type='button' onclick='addRow()'>+ Satır</button>
    <button class='green'>Kaydet</button>

    </form>

    </div>
    </div>

    <!-- ÇIKIŞ MODAL -->
    <div id='cikis' class='modal'>
    <div class='modal-content'>
    <h2>⬆️ Stok Çıkış</h2>

    <form method='POST' action='/cikis_ekle'>
    <select name='urun'>{''.join([f"<option>{x}</option>" for x in urunler])}</select>
    <select name='renk'>{''.join([f"<option>{x}</option>" for x in renkler])}</select>
    <input name='adet'>
    <button class='red'>Kaydet</button>
    </form>

    </div>
    </div>

    """

    return layout(html, "Depo - Stok")

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
