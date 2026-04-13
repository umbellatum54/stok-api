from flask import Blueprint, render_template, request, redirect
from datetime import datetime

try:
    from db import get_conn
    DB_VAR = True
except:
    DB_VAR = False

stok_bp = Blueprint("stok", __name__)


@stok_bp.route("/stok")
def stok():
    return render_template("stok.html")


# =========================
# STOK GİRİŞ (FULL PRO)
# =========================
@stok_bp.route("/stok-giris", methods=["GET", "POST"])
def stok_giris():

    if DB_VAR:
        conn = get_conn()
        cur = conn.cursor()

        # tablo garanti
        cur.execute("""
        CREATE TABLE IF NOT EXISTS hareket (
            id SERIAL PRIMARY KEY,
            urun TEXT,
            renk TEXT,
            adet INT,
            tarih TIMESTAMP
        )
        """)

        # ürün + renk çek
        cur.execute("SELECT ad, renk FROM urunler")
        data = cur.fetchall()

        urun_dict = {}
        for ad, renk in data:
            if ad not in urun_dict:
                urun_dict[ad] = []
            if renk:
                urun_dict[ad].append(renk)

        # ===== POST =====
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
            return redirect("/stok-giris")

        # SON 5 KAYIT
        cur.execute("""
        SELECT urun, renk, adet, tarih 
        FROM hareket 
        ORDER BY id DESC LIMIT 5
        """)
        son = cur.fetchall()

        # GÜNCEL STOK
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
