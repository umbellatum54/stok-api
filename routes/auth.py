from flask import Blueprint, render_template, request, redirect, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login():
    return render_template("login.html")

@auth_bp.route('/giris', methods=['POST'])
def giris():
    session["user"] = request.form.get("user")
    return redirect("/stok")
