# src/users/services.py
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from src import mysql
import MySQLdb.cursors

# Ekstensi file foto yang diizinkan oleh server
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UserService:

    @staticmethod
    def upload_foto(user_id, file):
        if file.filename == '':
            return {"error": "Tidak ada file yang dipilih"}, 400

        if file and allowed_file(file.filename):
            # Amankan nama file dari karakter berbahaya
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            
            # Tentukan lokasi penyimpanan ke folder static proyek
            upload_folder = os.path.join('static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Simpan path url foto profil baru ke database MySQL kolom avatar/photo
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET avatar = %s WHERE id = %s", (filename, user_id))
            mysql.connection.commit()
            cursor.close()

            return {"message": "Foto berhasil diunggah", "filename": filename}, 200
        
        return {"error": "Format file tidak diizinkan! (Gunakan PNG, JPG, JPEG)"}, 400

    @staticmethod
    def change_password(user_id, old_password, new_password, confirm_password):
        if not old_password or not new_password or not confirm_password:
            return {"error": "Semua kolom password wajib diisi"}, 400

        if new_password != confirm_password:
            return {"error": "Konfirmasi password baru tidak cocok"}, 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user or not user['password']:
            cursor.close()
            return {"error": "User tidak ditemukan atau menggunakan login Google"}, 400

        # Verifikasi password lama dengan hash database
        if not check_password_hash(user['password'], old_password):
            cursor.close()
            return {"error": "Password lama yang Anda masukkan salah"}, 400

        # Enkripsi password baru sebelum ditanam ke MySQL
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()

        return {"message": "Password berhasil diperbarui!"}, 200