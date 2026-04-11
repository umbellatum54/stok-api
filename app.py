from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# 🔹 DB bağlantı fonksiyonu
def get_conn():
    return psycopg2.connect(
        host="stokdb123.postgres.database.azure.com",
        database="postgres",
        user="adminuser2153@stokdb123",
        password="SIFREN",
        port=5432
    )

@app.route("/")
def home():
    return "Stok API çalışıyor"

@app.route("/ekle", methods=["POST"])
def ekle():
    try:
        conn = get_conn()
        cur = conn.cursor()

        urun = request.form.get("urun")
        adet = request.form.get("adet")
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

        # tablo yoksa oluştur
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

        return "Kaydedildi"

    except Exception as e:
        return str(e)

@app.route("/stok")
def stok():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT urun, adet, tarih FROM stok")
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
        return str(e)
