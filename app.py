from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

stoklar = []

@app.route("/")
def home():
    return """
    <h2>Stok Giriş Paneli</h2>
    <form action="/ekle" method="post">
        Ürün Adı: <input type="text" name="urun"><br><br>
        Adet: <input type="number" name="adet"><br><br>
        <button type="submit">Kaydet</button>
    </form>
    """

@app.route("/ekle", methods=["POST"])
def ekle():
    urun = request.form.get("urun")
    adet = request.form.get("adet")

    stoklar.append({
        "urun": urun,
        "adet": adet,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    return f"{urun} eklendi! <br><a href='/'>Geri dön</a>"

@app.route("/stok")
def stok():
    return jsonify(stoklar)
