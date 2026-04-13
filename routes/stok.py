from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime

# DB opsiyonel (çökmesin diye try)
try:
    from db import get_conn
    DB_VAR = True
except:
    DB_VAR = False

stok_bp = Blueprint("stok", __name__)


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

            return redirect("/urunler")

        cur.execute("SELECT id, ad, renk FROM urunler ORDER BY id DESC")
        urunler = cur.fetchall()

        cur.close()
        conn.close()

    else:
        # DB yoksa test veri
        urunler = [
            (1, "NO1", "BEJ"),
            (2, "NO1", "SİYAH")
        ]

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

    return redirect("/urunler")


# =========================
# STOK GİRİŞ
# =========================
@stok_bp.route("/stok-giris")
def stok_giris():

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT ad, renk FROM urunler ORDER BY ad")
        data = cur.fetchall()

        cur.close()
        conn.close()

        urun_dict = {}

        for ad, renk in data:
            if ad not in urun_dict:
                urun_dict[ad] = []
            if renk:
                urun_dict[ad].append(renk)

    else:
        # test veri
        urun_dict = {
            "NO1": ["BEJ", "SİYAH", "GRİ"],
            "NO3": ["BEYAZ", "SİYAH"]
        }

    return render_template("stok_giris.html", urun_dict=urun_dict)


# =========================
# STOK ÇIKIŞ
# =========================
@stok_bp.route("/stok-cikis", methods=["GET", "POST"])
def stok_cikis():

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT ad, renk FROM urunler ORDER BY ad")
        data = cur.fetchall()

        cur.close()
        conn.close()

        urun_dict = {}

        for ad, renk in data:
            if ad not in urun_dict:
                urun_dict[ad] = []
            if renk:
                urun_dict[ad].append(renk)

    else:
        urun_dict = {
            "NO1": ["BEJ", "SİYAH", "GRİ"],
            "NO3": ["BEYAZ", "SİYAH"]
        }

    if request.method == "POST":
        urun = request.form.get("urun")
        renk = request.form.get("renk")
        adet = request.form.get("adet")

        print("ÇIKIŞ:", urun, renk, adet)

        return redirect("/stok")

    return render_template("stok_cikis.html", urun_dict=urun_dict)


# =========================
# STOK ÖZET
# =========================
@stok_bp.route("/stok-ozet")
def stok_ozet():
    return render_template("stok_ozet.html")
