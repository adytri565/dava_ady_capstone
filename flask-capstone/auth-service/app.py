from flask import Flask, render_template, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Konfigurasi Flask (Mengarahkan ke folder templates dan static)
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')
app.secret_key = os.getenv("SECRET_KEY")


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["logisync_db"]

# 3. Konfigurasi Google OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
# ==========================================
# 4. ROUTE OTENTIKASI
# ==========================================

@app.route('/login')
def login_view():
    # Merender halaman HTML asli Anda
    return render_template('login.html')

@app.route('/api/auth/login/google')
def login_google():
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        session['user_email'] = user_info['email']
        session['user_name'] = user_info['name']
        session['user_picture'] = user_info['picture']
        
        db.users.update_one(
            {"email": user_info['email']},
            {"$set": {
                "name": user_info['name'],
                "email": user_info['email'],
                "status": "Active (Google SSO)"
            }},
            upsert=True
        )
        # Jika sukses login, lemparkan user kembali ke Gateway (Port 4000)
        return redirect('http://127.0.0.1:4000/dashboard')
    
    return redirect(url_for('login_view'))

@app.route('/api/auth/register-manual', methods=['POST'])
def register_manual():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return "Gagal: Email sudah terdaftar. Silakan kembali dan login."

    hashed_password = generate_password_hash(password)

    db.users.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password,
        "status": "Active (Manual)"
    })
    
    return redirect(url_for('login_view'))

@app.route('/api/auth/login-manual', methods=['POST'])
def login_manual():
    email = request.form.get('email')
    password = request.form.get('password')

    user = db.users.find_one({"email": email})
    
    if user and user.get("password") and check_password_hash(user["password"], password):
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        
        # Jika sukses login manual, lemparkan user ke Gateway
        return redirect('http://127.0.0.1:4000/dashboard')
    
    return "Gagal: Email atau Password salah!"

@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('login_view'))

# Dummy route untuk berjaga-jaga jika ada template yang mencari 'dashboard_view' di Auth
@app.route('/dashboard')
def dashboard_view():
    return redirect('http://127.0.0.1:4000/dashboard')

if __name__ == '__main__':
    app.run(port=5001, debug=True)