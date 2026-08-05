# src/users/controllers.py
from flask import request, redirect, session

from src.users import user_bp  # Mengambil user_bp dari __init__.py lokal folder users
from src.users.services import UserService

# =====================================================
# UPLOAD FOTO PROFIL
# =====================================================
@user_bp.route("/upload-foto", methods=["POST"])
def upload_foto():
    # Proteksi session langsung di dalam route untuk keamanan & efisiensi modular
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')

    user_id = request.form.get("user_id")
    file = request.files.get("foto")

    if not user_id or not file:
        return '<script>alert("Data upload tidak lengkap!"); window.history.back();</script>'

    result, status = UserService.upload_foto(user_id, file)

    if status != 200:
        return f'<script>alert("{result.get('error', 'Upload gagal')}"); window.history.back();</script>'

    # Paksa Flask reload data session id jika diperlukan
    session["user_id"] = int(user_id)

    return '<script>alert("Foto profil berhasil diperbarui!"); window.location="/api/admin/profile";</script>'


# =====================================================
# GANTI PASSWORD
# =====================================================
@user_bp.route("/change-password", methods=["POST"])
def change_password():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')

    user_id = request.form.get("user_id")
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    result, status = UserService.change_password(
        user_id=user_id,
        old_password=old_password,
        new_password=new_password,
        confirm_password=confirm_password
    )

    message = result.get("message") if status == 200 else result.get("error")
    return f'<script>alert("{message}"); window.location="/api/admin/profile";</script>'