# src/__init__.py
from flask import Flask
from authlib.integrations.flask_client import OAuth
import os

# 🌟 AMBIL MYSQL DARI EXTENSIONS
from src.extensions import db 

oauth = OAuth()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # ... semua app.config kamu di sini tetap sama ...
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-tugas-akhir")
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
    app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "capstone_db")
    
    # Hubungkan mysql ekstension ke app context
    mysql.init_app(app)
    oauth.init_app(app)
    
    # ... sisa kode registrasi google & blueprint ke bawah TETAP SAMA PERSIS ...
    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid profile email'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )
    
    from src.auth import auth_bp, init_oauth
    from src.auth import controllers        
    init_oauth(google)                      
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    from src.admin import admin_bp
    from src.admin import controllers       
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    
    from src.detection import detection_bp
    from src.detection import controllers   
    app.register_blueprint(detection_bp, url_prefix="/api/detection")
    
    from src.users import user_bp
    from src.users import controllers       
    app.register_blueprint(user_bp, url_prefix="/api/user")
    
    return app