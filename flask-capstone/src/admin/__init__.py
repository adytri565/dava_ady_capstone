# src/admin/__init__.py
from flask import Blueprint

# Daftarkan objek blueprint untuk admin command center
admin_bp = Blueprint('admin_bp', __name__)

# Load controller rute di bawahnya agar terikat ke admin_bp
from src.admin import controllers