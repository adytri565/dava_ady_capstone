# src/auth/controllers.py
from flask import render_template, redirect, url_for, session, request, jsonify
from src.extensions import mysql  # 👈 Ganti jadi ini
from src.auth import auth_bp  # Mengambil blueprint dari __init__.py lokal folder auth
import src.auth as auth_mod   # Untuk memanggil auth_mod.google_oauth

# 🌟 SINKRON: Impor fungsi dan model asli dari struktur foldermu
from src.auth.jwt_utils import generate_jwt
from src.auth.models import UserModel

from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

# =====================================================
# GERBANG REKAYASA HALAMAN WEB (WEB & ADMIN SIDE)
# =====================================================

@auth_bp.route('/login-page')
def login_page():
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/api/auth/login-page')

@auth_bp.route('/login-manual', methods=['POST'])
def login_manual():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # 🌟 SINKRON: Menggunakan UserModel untuk mengambil data user berdasarkan email
    try:
        # Menyesuaikan jika UserModel kamu punya pencarian by email, 
        # jika tidak ada, query cursor di bawah ini tetap menjadi backup aman.
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
    except Exception:
        user = None
    
    if user and user['password'] and check_password_hash(user['password'], password):
        # Tanam data ke Session untuk otentikasi Web Admin Dashboard (Peta & Driver)
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        return redirect('/api/admin/dashboard')
        
    return '<script>alert("Email atau Password salah!"); window.history.back();</script>'

# =====================================================
# API ENDPOINT KHUSUS FLUTTER MOBILE (JWT BASED)
# =====================================================

@auth_bp.route('/api/login', methods=['POST'])
def mobile_login():
    """
    Endpoint Login untuk Flutter Mobile App.
    Mengirim email & password -> Memvalidasi -> Mengembalikan JWT Token.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Email dan password wajib diisi!"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    
    # Validasi user dan password hash
    if user and user['password'] and check_password_hash(user['password'], password):
        # 🌟 SINKRON: Panggil fungsi asli generate_jwt dengan melempar data dictionary user
        try:
            token = generate_jwt(user)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Gagal membuat token: {str(e)}"}), 500
            
        return jsonify({
            "status": "success",
            "message": "Login mobile berhasil!",
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        }), 200
        
    return jsonify({"status": "error", "message": "Email atau password salah!"}), 401

# =====================================================
# GOOGLE OAUTH MANAGEMENT (WEB SIDE)
# =====================================================

@auth_bp.route('/login/google')
def login_google():
    return auth_mod.google_oauth.authorize_redirect(url_for('auth_bp.authorize_google', _external=True))

@auth_bp.route('/authorize/google')
def authorize_google():
    token = auth_mod.google_oauth.authorize_access_token()
    user_info = auth_mod.google_oauth.get('userinfo').json()
    email, name, google_id = user_info.get('email'), user_info.get('name'), user_info.get('id')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute("INSERT INTO users (name, email, google_id, role) VALUES (%s, %s, %s, 'admin')", (name, email, google_id))
        mysql.connection.commit()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
    cursor.close()
    
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_role'] = user['role']
    return redirect('/api/admin/dashboard')