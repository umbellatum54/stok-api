from flask import Flask, request, redirect, session, jsonify

import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"  # login için şart

# 🔥 VERİTABANI BAĞLANTI
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153",
        password="Deneme1234",
        port=5432,
        sslmode="require"
    )

# 🔹 LOGIN SAYFASI
@app.route('/')
def login_page():
    return '''
    <h2>Giriş Yap</h2>
    <form method="POST" action="/login">
        Kullanıcı: <input name="username"><br><br>
        Şifre: <input type="password" name="password"><br><br>
        <button>Giriş</button>
    </form>
    '''

# 🔹 LOGIN KONTROL
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "1234":
        session["user"] = username
        return redirect("/panel")
    else:
        return "Hatalı giriş!"

# 🔹 PANEL
@app.route('/panel')
def panel():
    if "user" not in session:
        return redirect("/")

    return '''
    <h2>Stok Paneli</h2>

    <form method="POST" action="/ekle">
        Ürün: <input name="urun"><br><br>
        Adet: <input type="number" name="adet"><br><br>
        <button>Kaydet</button>
    </form>

    <br><br>

    <a href="/stok">Stokları Gör</a><br>
    <a href="/logout">Çıkış Yap</a>
    '''

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

# 🔹 VERİ EKLE
@app.route('/ekle', methods=['POST'])
def ekle():
    if "user" not in session:
        return redirect("/")

    try:
        conn = get_conn()
        cur = conn.cursor()

        urun = request.form.get('urun')
        adet = int(request.form.get('adet'))
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

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
            (urun, adet, tarih)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/panel")

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 STOK LİSTE
@app.route('/stok')
def stok():
    if "user" not in session:
        return redirect("/")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT urun, adet, tarih FROM stok ORDER BY id DESC")
    rows = cur.fetchall()

    html = "<h2>Stok Listesi</h2><ul>"

    for r in rows:
        html += f"<li>{r[0]} - {r[1]} adet - {r[2]}</li>"

    html += "</ul><br><a href='/panel'>Geri</a>"

    return html
