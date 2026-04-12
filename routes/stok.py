from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from db import get_conn

stok_bp = Blueprint('stok', __name__)

@stok_bp.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS urunler (
            id SERIAL PRIMARY KEY,
            ad TEXT UNIQUE,
            renk TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hareket (
            id SERIAL PRIMARY KEY,
            urun TEXT,
            adet INT,
            tarih TIMESTAMP
        )
    """)

    cur.execute("SELECT * FROM urunler ORDER BY id DESC")
    urunler = cur.fetchall()

    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM urunler")
    stok_sayisi = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template("stok.html",
                           urunler=urunler,
                           logs=logs,
                           stok_sayisi=stok_sayisi)


@stok_bp.route('/urun-ekle', methods=['POST'])
def urun_ekle():
    ad = request.form.get('urun')
    renk = request.form.get('renk')

    conn = get_conn()
    cur = conn.cursor()

    # aynı ürün varsa ekleme
    cur.execute("SELECT * FROM urunler WHERE ad=%s AND renk=%s", (ad, renk))
    var = cur.fetchone()

    if not var:
        cur.execute("INSERT INTO urunler (ad, renk) VALUES (%s,%s)", (ad, renk))
        conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')
