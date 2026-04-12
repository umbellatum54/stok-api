@stok_bp.route('/urun-ekle', methods=['POST'])
def urun_ekle():
    ad = request.form['urun']
    renk = request.form['renk']

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO urunler (ad) VALUES (%s)", (ad,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')


@stok_bp.route('/stok-giris', methods=['POST'])
def stok_giris():
    urun = request.form['urun']
    adet = request.form['adet']

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO hareket (urun, adet, tarih) VALUES (%s,%s,%s)",
                (urun, adet, datetime.now()))
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')


@stok_bp.route('/stok-cikis', methods=['POST'])
def stok_cikis():
    urun = request.form['urun']
    adet = request.form['adet']

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO hareket (urun, adet, tarih) VALUES (%s,%s,%s)",
                (urun, -int(adet), datetime.now()))
    conn.commit()

    cur.close()
    conn.close()

    return redirect('/stok')
