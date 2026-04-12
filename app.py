from flask import Flask, request, redirect, session, send_from_directory
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "/tmp/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# DB CONNECTION
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
body {{margin:0;font-family:Arial;display:flex;background:#f4f6f9}}
.sidebar {{width:250px;background:#0f172a;color:white;height:100vh;padding:20px}}
.menu a {{display:block;color:white;padding:10px;text-decoration:none}}
.menu a:hover {{background:#1e293b}}
.main {{flex:1}}
.top {{background:#3c8dbc;color:white;padding:15px}}
.content {{padding:20px}}
.card {{background:white;padding:20px;border-radius:10px;margin-bottom:20px}}
button {{padding:10px;margin:5px;border:none;color:white;cursor:pointer}}
.green{{background:#00a65a}}
.red{{background:#dd4b39}}
.blue{{background:#3c8dbc}}
.orange{{background:#f39c12}}
table{{width:100%;border-collapse:collapse}}
td,th{{border:1px solid #ddd;padding:6px;text-align:center}}
.modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5)}}
.modal-content{{background:white;margin:5% auto;padding:20px;width:80%}}
</style>

<script>
function openModal(id){{document.getElementById(id).style.display='block'}}
function closeModal(id){{document.getElementById(id).style.display='none'}}

function addRow(){{
let div=document.getElementById("rows")
div.innerHTML+=div.children[0].outerHTML
}}
</script>
</head>

<body>

<div class="sidebar">
<h2>UMbellatum</h2>
<div class="menu">
<a href="/dashboard">Dashboard</a>
<a href="/stok">Depo - Stok</a>
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
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("SELECT COUNT(*) FROM urunler")
    u=cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM depo")
    d=cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM hareket WHERE tarih LIKE %s",
                (datetime.now().strftime("%Y-%m-%d")+"%",))
    i=cur.fetchone()[0]

    html=f"""
    <div class='card'>
    <h3>Dashboard</h3>
    <div>Stok Kart: {u}</div>
    <div>Depo: {d}</div>
    <div>Bugün İşlem: {i}</div>
    </div>
    """
    return layout(html,"Dashboard")

# STOK SAYFA
@app.route('/stok')
def stok():
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS depo(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS urunler(id SERIAL PRIMARY KEY, ad TEXT, renk TEXT, marka TEXT, kod TEXT, raf TEXT, depo TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS hareket(id SERIAL PRIMARY KEY, urun TEXT, renk TEXT, depo TEXT, adet INT, tip TEXT, tarih TEXT, userx TEXT)")

    cur.execute("SELECT DISTINCT ad FROM urunler")
    urunler=[x[0] for x in cur.fetchall()]

    cur.execute("SELECT DISTINCT renk FROM urunler")
    renkler=[x[0] for x in cur.fetchall()]

    cur.execute("SELECT ad FROM depo")
    depolar=[x[0] for x in cur.fetchall()]

    html="""

    <div class='card'>
    <h3>Hızlı İşlemler</h3>
    <button class='green' onclick="openModal('urun')">Ürün Kartı</button>
    <button class='blue' onclick="openModal('giris')">Üretim Girişi</button>
    <button class='red' onclick="openModal('cikis')">Stok Çıkış</button>
    <button class='orange' onclick="openModal('ozet')">Stok Durumu</button>
    </div>
    """

    # MODALS
    html+=f"""

<div id='urun' class='modal'><div class='modal-content'>
<h3>Ürün Kartı</h3>
<form method='POST' action='/urun'>
<input name='ad' placeholder='Ürün'>
<input name='renk' placeholder='Renk'>
<input name='marka' placeholder='Marka'>
<input name='kod' placeholder='Kod'>
<input name='raf' placeholder='Raf'>
<select name='depo'>
{''.join([f"<option>{d}</option>" for d in depolar])}
</select>
<button>Kaydet</button>
</form>
<button onclick="closeModal('urun')">Kapat</button>
</div></div>

<div id='giris' class='modal'><div class='modal-content'>
<h3>Üretim Girişi</h3>
<form method='POST' action='/giris_ekle'>
<div id='rows'>
<div>
<select name='urun'>
{''.join([f"<option>{u}</option>" for u in urunler])}
</select>
<select name='renk'>
{''.join([f"<option>{r}</option>" for r in renkler])}
</select>
<input name='adet'>
</div>
</div>
<button type='button' onclick='addRow()'>+ Satır</button>
<button>Kaydet</button>
</form>
<button onclick="closeModal('giris')">Kapat</button>
</div></div>

<div id='cikis' class='modal'><div class='modal-content'>
<h3>Stok Çıkış</h3>
<form method='POST' action='/cikis_ekle'>
<select name='urun'>
{''.join([f"<option>{u}</option>" for u in urunler])}
</select>
<select name='renk'>
{''.join([f"<option>{r}</option>" for r in renkler])}
</select>
<input name='adet'>
<button>Kaydet</button>
</form>
<button onclick="closeModal('cikis')">Kapat</button>
</div></div>

"""

    # LOG
    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs=cur.fetchall()

    html+="<div class='card'><h3>Son İşlemler</h3><table>"
    html+="<tr><th>Ürün</th><th>Renk</th><th>Depo</th><th>Adet</th><th>Tip</th><th>Tarih</th><th>Kullanıcı</th></tr>"

    for l in logs:
        html+=f"<tr><td>{l[1]}</td><td>{l[2]}</td><td>{l[3]}</td><td>{l[4]}</td><td>{l[5]}</td><td>{l[6]}</td><td>{l[7]}</td></tr>"

    html+="</table></div>"

    return layout(html,"Depo - Stok")

# ACTIONS
@app.route('/urun',methods=['POST'])
def urun():
    conn=get_conn()
    cur=conn.cursor()
    cur.execute("INSERT INTO urunler(ad,renk,marka,kod,raf,depo) VALUES(%s,%s,%s,%s,%s,%s)",
                (request.form['ad'],request.form['renk'],request.form['marka'],request.form['kod'],request.form['raf'],request.form['depo']))
    conn.commit()
    return redirect("/stok")

@app.route('/giris_ekle',methods=['POST'])
def giris_ekle():
    conn=get_conn()
    cur=conn.cursor()

    urun=request.form.getlist('urun')
    renk=request.form.getlist('renk')
    adet=request.form.getlist('adet')

    for i in range(len(urun)):
        cur.execute("INSERT INTO hareket(urun,renk,depo,adet,tip,tarih,userx) VALUES(%s,%s,'Depo',%s,'Giriş',%s,%s)",
                    (urun[i],renk[i],adet[i],datetime.now(),session.get("user")))

    conn.commit()
    return redirect("/stok")

@app.route('/cikis_ekle',methods=['POST'])
def cikis_ekle():
    conn=get_conn()
    cur=conn.cursor()
    cur.execute("INSERT INTO hareket(urun,renk,depo,adet,tip,tarih,userx) VALUES(%s,%s,'Depo',%s,'Çıkış',%s,%s)",
                (request.form['urun'],request.form['renk'],request.form['adet'],datetime.now(),session.get("user")))
    conn.commit()
    return redirect("/stok")
