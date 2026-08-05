# src/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__)
google_oauth = None

def init_oauth(google_instance):
    global google_oauth
    google_oauth = google_instance