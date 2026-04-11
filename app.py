from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

conn = psycopg2.connect(
    host="stokdb123.postgres.database.azure.com",
    database="postgres",
    user="adminuser2153@stokdb123",
    password="GnyMrt215354!.!1",
    port=5432
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stok (
    id SERIAL PRIMARY KEY,
    urun TEXT,
    adet INTEGER,
    tarih TEXT
)
""")
conn.commit()

@app.route("/")
def home():
    return """
    <h2>Stok Giriş Paneli</h2>
    <form action="/ekle" method="post">
        Ürün Adı: <input type="text" name="urun"><br><br>
        Adet: <input type="number" name="adet"><br><br>
        <button type="submit">Kaydet</button>
    </form>
    """

@app.route("/ekle", methods=["POST"])
def ekle():
    urun = request.form.get("urun")
    adet = request.form.get("adet")
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
        "INSERT INTO stok (urun, adet, tarih) VALUES (%s, %s, %s)",
        (urun, adet, tarih)
    )
    conn.commit()

    return f"{urun} eklendi! <br><a href='/'>Geri dön</a>"

@app.route("/stok")
def stok():
    cur.execute("SELECT urun, adet, tarih FROM stok")
    rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "urun": r[0],
            "adet": r[1],
            "tarih": r[2]
        })

    return jsonify(data)
