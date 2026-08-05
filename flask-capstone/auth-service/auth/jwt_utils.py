# src/auth/jwt_utils.py
import jwt
from datetime import datetime, timedelta
from flask import current_app

from src.auth.models import UserModel

# =====================================================
# INTERNAL: AMBIL JWT SECRET DENGAN AMAN
# =====================================================
def _get_jwt_secret():
    """
    Ambil JWT_SECRET_KEY dari app.config dengan aman.
    Tidak akan KeyError, tapi error yang jelas.
    """
    secret = current_app.config.get("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY belum diset di app.config. "
            "Pastikan create_app() dijalankan dengan benar."
        )
    return secret


# =====================================================
# GENERATE JWT (Untuk Dikirim ke Flutter)
# =====================================================
def generate_jwt(user):
    """
    Generate JWT untuk user.
    HARUS dipanggil di dalam request / app context.
    """
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7), # Token aktif selama 7 hari
    }

    token = jwt.encode(
        payload,
        _get_jwt_secret(),
        algorithm="HS256",
    )

    return token


# =====================================================
# DECODE JWT (Membaca Token dari Flutter)
# =====================================================
def decode_jwt(token):
    """
    Decode JWT.
    Return payload jika valid, None jika invalid/kadaluarsa.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=["HS256"],
        )
        return payload

    except jwt.ExpiredSignatureError:
        # Token kadaluarsa (sudah lewat 7 hari)
        return None

    except jwt.InvalidTokenError:
        # Token rusak / palsu / hasil manipulasi
        return None


# =====================================================
# GET USER FROM JWT (Validasi Sesi Driver Mobile)
# =====================================================
def get_user_from_token(token):
    """
    Ambil user dari JWT.
    Return user dict atau None.
    """
    payload = decode_jwt(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    # Mengambil data objek user real-time dari UserModel di atas
    user = UserModel.get_user_by_id(user_id)
    if not user:
        return None

    # Proteksi tambahan jika akun di-suspend/nonaktifkan oleh admin
    if user.get("is_active") is False:
        return None

    return user