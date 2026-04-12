from flask import Flask, request, redirect, session
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

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
    return f"""
    <html>
    <body style='display:flex;font-family:Arial'>
    <div style='width:200px;background:#111;color:white;padding:10px'>
        <h3>Menu</h3>
        <a href='/dashboard' style='color:white'>Dashboard</a><br>
        <a href='/stok' style='color:white'>Stok</a>
    </div>
    <div style='flex:1;padding:20px'>
    <h2>{title}</h2>
    {content}
    </div>
    </body>
    </html>
    """

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    conn = get_conn()
    cur = conn.cursor()

    # TABLO GARANTİ
    cur.execute("CREATE TABLE IF NOT EXISTS urunler(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS depo(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS hareket(id SERIAL PRIMARY KEY, urun TEXT, adet INT, tarih TEXT)")

    # SAFE COUNT
    cur.execute("SELECT COUNT(*) FROM urunler")
    u = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM depo")
    d = cur.fetchone()[0] or 0

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM hareket WHERE tarih LIKE %s", (today+"%",))
    i = cur.fetchone()[0] or 0

    html = f"""
    <div>Stok Kart: {u}</div>
    <div>Depo: {d}</div>
    <div>Bugün İşlem: {i}</div>
    """

    return layout(html)

# STOK
@app.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    # TABLO GARANTİ
    cur.execute("CREATE TABLE IF NOT EXISTS depo(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS urunler(id SERIAL PRIMARY KEY, ad TEXT, renk TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS hareket(id SERIAL PRIMARY KEY, urun TEXT, renk TEXT, adet INT, tip TEXT, tarih TEXT, userx TEXT)")

    # VERİLER
    cur.execute("SELECT ad FROM urunler")
    urunler = [x[0] for x in cur.fetchall()] or ["Ürün Yok"]

    cur.execute("SELECT DISTINCT renk FROM urunler")
    renkler = [x[0] for x in cur.fetchall()] or ["Renk Yok"]

    html = f"""
    <h3>Hızlı İşlemler</h3>
    <form method='POST' action='/giris_ekle'>
    Ürün: <select name='urun'>
    {''.join([f"<option>{u}</option>" for u in urunler])}
    </select>
    Renk: <select name='renk'>
    {''.join([f"<option>{r}</option>" for r in renkler])}
    </select>
    Adet: <input name='adet'>
    <button>Giriş</button>
    </form>
    """

    return layout(html)

# GİRİŞ
@app.route('/giris_ekle', methods=['POST'])
def giris_ekle():
    conn = get_conn()
    cur = conn.cursor()

    tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute("""
    INSERT INTO hareket (urun,renk,adet,tip,tarih,userx)
    VALUES (%s,%s,%s,'Giriş',%s,%s)
    """, (
        request.form.get('urun'),
        request.form.get('renk'),
        int(request.form.get('adet') or 0),
        tarih,
        session.get("user")
    ))

    conn.commit()
    return redirect("/stok")
