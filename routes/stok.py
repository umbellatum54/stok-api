from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from db import get_conn

stok_bp = Blueprint("stok", __name__, url_prefix="/depo-stok")


# =========================
# ANA SAYFA
# =========================
@stok_bp.route("/")
def stok():
    return render_template("stok.html")


# =========================
# ÜRÜNLER
# =========================
@stok_bp.route("/urunler", methods=["GET", "POST"])
def urunler():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT
    )
    """)

    if request.method == "POST":
        ad = request.form.get("ad")
        renk = request.form.get("renk")

        if ad and renk:
            cur.execute(
                "INSERT INTO urunler (ad, renk) VALUES (%s,%s)",
                (ad, renk)
            )
            conn.commit()

        return redirect("/depo-stok/urunler")

    cur.execute("SELECT id, ad, renk FROM urunler ORDER BY id DESC")
    urunler = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("urunler.html", urunler=urunler)


# =========================
# STOK GİRİŞ
# =========================
@stok_bp.route("/stok-giris", methods=["GET", "POST"])
def stok_giris():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hareket (
        id SERIAL PRIMARY KEY,
        urun TEXT,
        renk TEXT,
        adet INT,
        tarih TIMESTAMP
    )
    """)

    cur.execute("SELECT ad, renk FROM urunler")
    data = cur.fetchall()

    urun_dict = {}
    for ad, renk in data:
        urun_dict.setdefault(ad, []).append(renk)

    if request.method == "POST":

        for i in range(1, 6):

            urun = request.form.get(f"urun{i}")
            renk = request.form.get(f"renk{i}")
            adet = request.form.get(f"adet{i}")

            # 🔥 KRİTİK FIX (PATLAMAYI ENGELLER)
            if not urun or not renk or not adet:
                continue

            try:
                adet = int(adet)
            except:
                continue

            cur.execute("""
            INSERT INTO hareket (urun, renk, adet, tarih)
            VALUES (%s,%s,%s,%s)
            """, (urun, renk, adet, datetime.now()))

        conn.commit()
        return redirect("/depo-stok/stok-giris")

    # SON KAYIT
    cur.execute("""
    SELECT urun, renk, adet, tarih
    FROM hareket ORDER BY id DESC LIMIT 5
    """)
    son = cur.fetchall()

    # STOK
    cur.execute("""
    SELECT urun, renk, SUM(adet)
    FROM hareket
    GROUP BY urun, renk
    """)
    stoklar = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "stok_giris.html",
        urun_dict=urun_dict,
        son=son,
        stoklar=stoklar
    )


# =========================
# STOK ÇIKIŞ
# =========================
@stok_bp.route("/stok-cikis", methods=["GET", "POST"])
def stok_cikis():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT ad, renk FROM urunler")
    data = cur.fetchall()

    urun_dict = {}
    for ad, renk in data:
        urun_dict.setdefault(ad, []).append(renk)

    if request.method == "POST":

        urun = request.form.get("urun")
        renk = request.form.get("renk")
        adet = request.form.get("adet")

        if urun and renk and adet:
            try:
                adet = int(adet)
            except:
                adet = 0

            cur.execute("""
            INSERT INTO hareket (urun, renk, adet, tarih)
            VALUES (%s,%s,%s,%s)
            """, (urun, renk, -adet, datetime.now()))

            conn.commit()

        return redirect("/depo-stok/stok-cikis")

    cur.close()
    conn.close()

    return render_template("stok_cikis.html", urun_dict=urun_dict)


# =========================
# STOK ÖZET
# =========================
@stok_bp.route("/stok-ozet")
def stok_ozet():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT urun, renk, SUM(adet)
    FROM hareket
    GROUP BY urun, renk
    """)
    stoklar = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("stok_ozet.html", stoklar=stoklar)
