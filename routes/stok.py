from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from db import get_conn

stok_bp = Blueprint('stok', __name__)


# 📊 STOK PANELİ
@stok_bp.route('/stok')
def stok():
    conn = get_conn()
    cur = conn.cursor()

    # tablolar yoksa oluştur
    cur.execute("""
        CREATE TABLE IF NOT EXISTS urunler (
            id SERIAL PRIMARY KEY,
            ad TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS depo (
            id SERIAL PRIMARY KEY,
            ad TEXT
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

    # veriler
    cur.execute("SELECT COUNT(*) FROM urunler")
    stok_sayisi = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM depo")
    depo_sayisi = cur.fetchone()[0]

    cur.execute("SELECT * FROM hareket ORDER BY id DESC LIMIT 10")
    logs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "stok.html",
        stok_sayisi=stok_sayisi,
        depo_sayisi=depo_sayisi,
        logs=logs
    )


# ➕ ÜRÜN EKLE
@stok_bp.route('/urun-ekle', methods=['POST'])
def urun_ekle():
    ad = request.form.get('urun')

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO urunler (ad) VALUES (%s)", (ad,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')


# 📥 STOK GİRİŞ
@stok_bp.route('/stok-giris', methods=['POST'])
def stok_giris():
    urun = request.form.get('urun')
    adet = request.form.get('adet')

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO hareket (urun, adet, tarih) VALUES (%s,%s,%s)",
        (urun, int(adet), datetime.now())
    )
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')


# 📤 STOK ÇIKIŞ
@stok_bp.route('/stok-cikis', methods=['POST'])
def stok_cikis():
    urun = request.form.get('urun')
    adet = request.form.get('adet')

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO hareket (urun, adet, tarih) VALUES (%s,%s,%s)",
        (urun, -int(adet), datetime.now())
    )
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')
