from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>Stok Giriş</h2>
    <form method="POST" action="/ekle">
        Ürün Adı: <input type="text" name="urun"><br><br>
        Adet: <input type="number" name="adet"><br><br>
        <button type="submit">Kaydet</button>
    </form>
    '''

@app.route('/ekle', methods=['POST'])
def ekle():
    urun = request.form.get('urun')
    adet = request.form.get('adet')

    return f"{urun} ürününden {adet} adet kaydedildi!"
