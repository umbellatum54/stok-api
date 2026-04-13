from flask import Blueprint, render_template, request, redirect
from datetime import datetime

try:
    from db import get_conn
    DB_VAR = True
except:
    DB_VAR = False

stok_bp = Blueprint("stok", __name__, url_prefix="/depo-stok")


# =========================
# ANA SAYFA
# =========================
@stok_bp.route("/")
def stok():
    return render_template("stok.html")


# =========================
# STOK GİRİŞ
# =========================
@stok_bp.route("/stok-giris", methods=["GET", "POST"])
def stok_giris():

    urun_dict = {}
    son = []
    stoklar = []

    if DB_VAR:
        try:
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id SERIAL PRIMARY KEY,
                ad TEXT,
                renk TEXT
            )
            """)

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

            for ad, renk in data:
                urun_dict.setdefault(ad, []).append(renk)

            # POST
            if request.method == "POST":
                for i in range(1, 6):
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

        except Exception as e:
            print("HATA:", e)

    return render_template(
        "stok_giris.html",
        urun_dict=urun_dict,
        son=son,
        stoklar=stoklar
    )


# =========================
# STOK ÖZET
# =========================
@stok_bp.route("/stok-ozet")
def stok_ozet():

    stoklar = []

    if DB_VAR:
        try:
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

        except Exception as e:
            print("HATA:", e)

    return render_template("stok_ozet.html", stoklar=stoklar)


# =========================
# STOK ÇIKIŞ
# =========================
@stok_bp.route("/stok-cikis", methods=["GET","POST"])
def stok_cikis():

    urun_dict = {}

    if DB_VAR:
        try:
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("SELECT ad, renk FROM urunler")
            data = cur.fetchall()

            for ad, renk in data:
                urun_dict.setdefault(ad, []).append(renk)

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

        except Exception as e:
            print("HATA:", e)

    return render_template("stok_cikis.html", urun_dict=urun_dict)
