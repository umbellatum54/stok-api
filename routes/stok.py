from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime

stok_bp = Blueprint('stok', __name__)


@stok_bp.route('/stok')
def stok():
    return render_template("stok.html")


@stok_bp.route('/stok-giris')
def stok_giris_page():
    return render_template("stok_giris.html")


@stok_bp.route('/stok-cikis')
def stok_cikis_page():
    return render_template("stok_cikis.html")


@stok_bp.route('/stok-ozet')
def stok_ozet_page():
    return render_template("stok_ozet.html")
