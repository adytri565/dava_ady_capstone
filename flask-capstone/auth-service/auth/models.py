# src/auth/models.py
from src import mysql
import MySQLdb.cursors

class UserModel:
    @staticmethod
    def get_user_by_id(user_id):
        """
        Mengambil data user berdasarkan ID dari database.
        Digunakan oleh fungsi jwt_utils.get_user_from_token()
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, name, email, role, is_active FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        # Jika di database kamu belum ada kolom 'is_active', 
        # baris di bawah ini bertugas memastikan sistem tidak error (fallback safe)
        if user and 'is_active' not in user:
            user['is_active'] = True
            
        return user

    @staticmethod
    def get_user_by_email(email):
        """
        Mengambil data user lengkap berdasarkan email untuk keperluan validasi login.
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user