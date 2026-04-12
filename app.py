from flask import Flask, request, redirect, session, jsonify
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret123"

# 🔥 session süresi (beni hatırla)
app.permanent_session_lifetime = timedelta(days=7)

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

# 🔹 LOGIN SAYFASI (MODERN)
@app.route('/')
def login_page():
    return '''
    <html>
    <head>
        <title>Giriş</title>
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(135deg, #f0f2f5, #e4efe9);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .box {
                width: 360px;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
            }

            .logo {
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }

            h2 {
                margin-bottom: 20px;
            }

            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 12px;
                margin-top: 8px;
                margin-bottom: 15px;
                border-radius: 8px;
                border: 1px solid #ddd;
            }

            .remember {
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 13px;
                margin-bottom: 15px;
            }

            button {
                width: 100%;
                padding: 12px;
                background: #7ED957;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }

            button:hover {
                background: #6fd14b;
            }

            .forgot {
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>

        <form class="box" method="POST" action="/login">
            <div class="logo">UMbellatum</div>
            <h2>Tekrar Hoş Geldiniz!</h2>

            <input type="text" name="username" placeholder="E-posta adresi">

            <input type="password" name="password" placeholder="Şifre">

            <div class="remember">
                <label>
                    <input type="checkbox" name="remember"> Beni hatırla
                </label>
                <div class="forgot">Şifremi Unuttum</div>
            </div>

            <button>Giriş Yap</button>
        </form>

    </body>
    </html>
    '''

# 🔹 LOGIN
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember")

    if username == "admin" and password == "1234":
        session["user"] = username

        if remember:
            session.permanent = True

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
