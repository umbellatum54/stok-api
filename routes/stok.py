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

    # TÜM ÜRÜN + RENK
    cur.execute("SELECT ad, renk FROM urunler ORDER BY ad")
    data = cur.fetchall()

    cur.close()
    conn.close()

    # PYTHON → DICT YAPISI
    urun_dict = {}

    for ad, renk in data:
        if ad not in urun_dict:
            urun_dict[ad] = []
        if renk:
            urun_dict[ad].append(renk)

    return render_template("stok_giris.html", urun_dict=urun_dict)


# =========================
# STOK ÇIKIŞ
# =========================
@stok_bp.route("/stok-cikis", methods=["GET", "POST"])
def stok_cikis():
    conn = get_conn()
    cur = conn.cursor()

    # ÜRÜN + RENK çek
    cur.execute("SELECT ad, renk FROM urunler ORDER BY ad")
    data = cur.fetchall()

    # ürün → renk map
    urun_dict = {}
    for ad, renk in data:
        if ad not in urun_dict:
            urun_dict[ad] = []
        if renk:
            urun_dict[ad].append(renk)

    # POST (şimdilik sadece test)
    if request.method == "POST":
        urun = request.form.get("urun")
        renk = request.form.get("renk")
        adet = request.form.get("adet")

        print("ÇIKIŞ:", urun, renk, adet)

        return redirect("/stok")

    cur.close()
    conn.close()

    return render_template("stok_cikis.html", urun_dict=urun_dict)


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
