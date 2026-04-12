from flask import Blueprint, render_template
from db import get_conn

stok_bp = Blueprint('stok', __name__)

@stok_bp.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS urunler(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS depo(id SERIAL PRIMARY KEY, ad TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS hareket(id SERIAL PRIMARY KEY, urun TEXT, adet INT, tarih TEXT)")

    cur.execute("SELECT COUNT(*) FROM urunler")
    stok_sayisi = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM depo")
    depo_sayisi = cur.fetchone()[0]

    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("stok.html",
                           stok_sayisi=stok_sayisi,
                           depo_sayisi=depo_sayisi,
                           logs=logs)
