from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from db import get_conn

stok_bp = Blueprint('stok', __name__)


# 📦 ANA STOK SAYFASI
@stok_bp.route('/stok-giris')
def stok_giris_page():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT ad, renk FROM urunler")
    except:
        # eski tabloysa (renk yoksa)
        cur.execute("SELECT ad, '' as renk FROM urunler")

    rows = cur.fetchall()

    urun_map = {}

    for r in rows:
        ad = r[0]
        renk = r[1] if len(r) > 1 else ""

        if ad not in urun_map:
            urun_map[ad] = []

        if renk and renk not in urun_map[ad]:
            urun_map[ad].append(renk)

    cur.close()
    conn.close()

    return render_template("stok_giris.html", urun_map=urun_map)


# 📄 ÜRÜN SAYFASI
@stok_bp.route('/urunler')
def urunler_page():
    conn = get_conn()
    cur = conn.cursor()

    # kolon eksikse ekle (KRİTİK!)
    cur.execute("ALTER TABLE urunler ADD COLUMN IF NOT EXISTS renk TEXT")

    cur.execute("SELECT * FROM urunler ORDER BY id DESC")
    urunler = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("urunler.html", urunler=urunler)


# ➕ ÜRÜN EKLE
@stok_bp.route('/urun-ekle', methods=['POST'])
def urun_ekle():
    ad = request.form.get('urun')
    renk = request.form.get('renk')

    conn = get_conn()
    cur = conn.cursor()

    # tablo garanti
    cur.execute("ALTER TABLE urunler ADD COLUMN IF NOT EXISTS renk TEXT")

    # tekrar kontrol
    cur.execute("SELECT * FROM urunler WHERE ad=%s AND renk=%s", (ad, renk))
    if not cur.fetchone():
        cur.execute("INSERT INTO urunler (ad, renk) VALUES (%s,%s)", (ad, renk))
        conn.commit()

    cur.close()
    conn.close()

    return redirect('/urunler')


# 📥 STOK GİRİŞ SAYFASI
@stok_bp.route('/stok-giris')
def stok_giris_page():
    conn = get_conn()
    cur = conn.cursor()

    # kolon garanti
    cur.execute("ALTER TABLE urunler ADD COLUMN IF NOT EXISTS renk TEXT")

    cur.execute("SELECT ad, renk FROM urunler")
    rows = cur.fetchall()

    urun_map = {}

    for r in rows:
        ad = r[0]
        renk = r[1] if r[1] else ""

        if ad not in urun_map:
            urun_map[ad] = []

        if renk and renk not in urun_map[ad]:
            urun_map[ad].append(renk)

    cur.close()
    conn.close()

    return render_template("stok_giris.html", urun_map=urun_map)


# 📥 TOPLU STOK GİRİŞ
@stok_bp.route('/stok-toplu-giris', methods=['POST'])
def stok_toplu():
    conn = get_conn()
    cur = conn.cursor()

    kullanici = session.get("user", "admin")

    for i in range(1, 11):
        urun = request.form.get(f"urun{i}")
        renk = request.form.get(f"renk{i}")
        adet = request.form.get(f"adet{i}")

        if urun and adet:
            cur.execute("""
                INSERT INTO hareket (urun, renk, adet, kullanici, tarih)
                VALUES (%s,%s,%s,%s,%s)
            """, (urun, renk, int(adet), kullanici, datetime.now()))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/stok')


# 📤 STOK ÇIKIŞ SAYFASI
@stok_bp.route('/stok-cikis')
def stok_cikis_page():
    return render_template("stok_cikis.html")


# 📊 STOK ÖZET
@stok_bp.route('/stok-ozet')
def stok_ozet_page():
    return render_template("stok_ozet.html")
