from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime

stok_bp = Blueprint('stok', __name__)


# ANA SAYFA
@stok_bp.route('/stok')
def stok():
    return render_template("stok.html")


# ÜRÜN KARTLARI
@stok_bp.route('/urunler')
def urunler():
    return render_template("urunler.html")


# STOK GİRİŞ
@stok_bp.route('/stok-giris')
def stok_giris():
    return render_template("stok_giris.html")


# STOK ÇIKIŞ
@stok_bp.route('/stok-cikis')
def stok_cikis():
    return render_template("stok_cikis.html")


# STOK ÖZET
@stok_bp.route('/stok-ozet')
def stok_ozet():
    return render_template("stok_ozet.html")
