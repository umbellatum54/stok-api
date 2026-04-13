from flask import Flask
from routes.auth import auth_bp
from routes.stok import stok_bp

app = Flask(__name__)
app.secret_key = "secret123"

# 🔥 DEBUG EKLEDİK (önemli)
app.config["DEBUG"] = True

# 🔥 REGISTER
app.register_blueprint(auth_bp)
app.register_blueprint(stok_bp)

# TEST ROUTE (çok önemli)
@app.route("/test")
def test():
    return "ÇALIŞIYOR"

if __name__ == "__main__":
    app.run()
