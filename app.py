from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# 🔥 VERİTABANI BAĞLANTI
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153"
        password="GnyMrt215354!.!1",
        port=5432,
        sslmode="require"
    )

# 🔹 ANA SAYFA (FORM)
@app.route('/')
def home():
    return '''
    <h2>Stok Giriş</h2>
    <form method="POST" action="/ekle">
        Ürün Adı: <input type="text" name="urun"><br><br>
        Adet: <input type="number" name="adet"><br><br>
        <button type="submit">Kaydet</button>
    </form>
    '''

# 🔹 VERİ EKLE
@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        conn = get_conn()
        cur = conn.cursor()

        urun = request.form.get('urun')
        adet = int(request.form.get('adet'))
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

        # tablo oluştur
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stok (
                id SERIAL PRIMARY KEY,
                urun TEXT,
                adet INTEGER,
                tarih TEXT
            )
        """)

        # veri ekle
        cur.execute(
            "INSERT INTO stok (urun, adet, tarih) VALUES (%s, %s, %s)",
            (urun, adet, tarih)
        )

        conn.commit()
        cur.close()
        conn.close()

        return f"{urun} kaydedildi!"

    except Exception as e:
        return f"HATA: {str(e)}"

# 🔹 STOK LİSTE
@app.route('/stok')
def stok():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT urun, adet, tarih FROM stok ORDER BY id DESC")
        rows = cur.fetchall()

        data = []
        for r in rows:
            data.append({
                "urun": r[0],
                "adet": r[1],
                "tarih": r[2]
            })

        cur.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return f"HATA: {str(e)}"
