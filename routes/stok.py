from flask import Blueprint, render_template, request, redirect
from datetime import datetime

try:
    from db import get_conn
    DB_VAR = True
except:
    DB_VAR = False

# 🔥 ÖNEMLİ: URL PREFIX EKLENDİ
stok_bp = Blueprint("stok", __name__, url_prefix="/depo-stok")


# =========================
# ANA SAYFA
# =========================
@stok_bp.route("/stok")
def stok():
    return render_template("stok.html")


# =========================
# ÜRÜN KARTLARI
# =========================
@stok_bp.route("/urunler", methods=["GET", "POST"])
def urunler():

    if DB_VAR:
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

    else:
        urunler = [(1,"NO1","BEJ")]

    return render_template("urunler.html", urunler=urunler)


# =========================
# ÜRÜN SİL
# =========================
@stok_bp.route("/urun-sil/<int:id>")
def urun_sil(id):

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("DELETE FROM urunler WHERE id=%s", (id,))
        conn.commit()

        cur.close()
        conn.close()

    return redirect("/depo-stok/urunler")


# =========================
# STOK GİRİŞ
# =========================
@stok_bp.route("/stok-giris", methods=["GET", "POST"])
def stok_giris():

    if DB_VAR:
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
            if ad not in urun_dict:
                urun_dict[ad] = []
            if renk:
                urun_dict[ad].append(renk)

        if request.method == "POST":

            for i in range(1,6):
                urun = request.form.get(f"urun{i}")
                renk = request.form.get(f"renk{i}")
                adet = request.form.get(f"adet{i}")

                if urun and renk and adet:
                    cur.execute("""
                    INSERT INTO hareket (urun, renk, adet, tarih)
                    VALUES (%s,%s,%s,%s)
                    """, (urun, renk, int(adet), datetime.now()))

            conn.commit()
            return redirect("/depo-stok/stok-giris")

        cur.execute("""
        SELECT urun, renk, adet, tarih 
        FROM hareket 
        ORDER BY id DESC LIMIT 5
        """)
        son = cur.fetchall()

        cur.execute("""
        SELECT urun, renk, SUM(adet) 
        FROM hareket
        GROUP BY urun, renk
        """)
        stoklar = cur.fetchall()

        cur.close()
        conn.close()

    else:
        urun_dict = {"NO1":["BEJ","SİYAH"]}
        son = []
        stoklar = []

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

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT ad, renk FROM urunler")
        data = cur.fetchall()

        urun_dict = {}
        for ad, renk in data:
            if ad not in urun_dict:
                urun_dict[ad] = []
            if renk:
                urun_dict[ad].append(renk)

        if request.method == "POST":

            urun = request.form.get("urun")
            renk = request.form.get("renk")
            adet = request.form.get("adet")

            if urun and renk and adet:
                cur.execute("""
                INSERT INTO hareket (urun, renk, adet, tarih)
                VALUES (%s,%s,%s,%s)
                """, (urun, renk, -int(adet), datetime.now()))

            conn.commit()
            return redirect("/depo-stok/stok-cikis")

        cur.close()
        conn.close()

    else:
        urun_dict = {"NO1":["BEJ","SİYAH"]}

    return render_template("stok_cikis.html", urun_dict=urun_dict)


# =========================
# STOK ÖZET
# =========================
@stok_bp.route("/stok-ozet")
def stok_ozet():

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
        SELECT urun, renk, SUM(adet) 
        FROM hareket
        GROUP BY urun, renk
        ORDER BY urun
        """)

        stoklar = cur.fetchall()

        cur.close()
        conn.close()

    else:
        stoklar = [("NO1","BEJ",10)]

    return render_template("stok_ozet.html", stoklar=stoklar)
