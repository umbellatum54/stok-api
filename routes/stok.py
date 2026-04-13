from flask import Blueprint, render_template, request, redirect
from db import get_conn

stok_bp = Blueprint("stok", __name__)

# =========================
# ANA SAYFA
# =========================
@stok_bp.route("/stok")
def stok():
    return render_template("stok.html")


# =========================
# ÜRÜN KARTLARI SAYFASI
# =========================
@stok_bp.route("/urunler", methods=["GET", "POST"])
def urunler():
    conn = get_conn()
    cur = conn.cursor()

    # TABLO YOKSA OLUŞTUR
    cur.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id SERIAL PRIMARY KEY,
        ad TEXT,
        renk TEXT
    )
    """)

    # KAYDET
    if request.method == "POST":
        ad = request.form.get("ad")
        renk = request.form.get("renk")

        if ad and renk:
            cur.execute(
                "INSERT INTO urunler (ad, renk) VALUES (%s, %s)",
                (ad, renk)
            )
            conn.commit()

        return redirect("/urunler")

    # LİSTELE
    cur.execute("SELECT id, ad, renk FROM urunler ORDER BY id DESC")
    urunler = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("urunler.html", urunler=urunler)


# =========================
# STOK GİRİŞ
# =========================
@stok_bp.route("/stok-giris")
def stok_giris():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT ad FROM urunler ORDER BY ad")
    urunler = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("stok_giris.html", urunler=urunler)


# =========================
# STOK ÇIKIŞ
# =========================
@stok_bp.route("/stok-cikis")
def stok_cikis():
    return render_template("stok_cikis.html")


# =========================
# STOK ÖZET
# =========================
@stok_bp.route("/stok-ozet")
def stok_ozet():
    return render_template("stok_ozet.html")


# =========================
# ÜRÜN SİL
# =========================
@stok_bp.route("/urun-sil/<int:id>")
def urun_sil(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM urunler WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect("/urunler")
