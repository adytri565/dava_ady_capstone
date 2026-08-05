# src/detection/controllers.py
from flask import request, jsonify
from src.detection import detection_bp
from src.extensions import mysql  # 🌟 AMAN: Mengambil dari extensions netral
import MySQLdb.cursors

@detection_bp.route('/report', methods=['POST'])
def report_detection():
    """
    Endpoint menerima data telemetri real-time dari Postman, 
    skrip Python lokal (test_camera.py), maupun aplikasi Flutter Mobile.
    """
    # 1. Ambil data JSON kiriman client
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "Payload JSON tidak ditemukan!"}), 400
        
    # 2. Ekstrak parameter sesuai format payload kamu
    driver_id = data.get('driver_id')
    event_type = data.get('event_type')
    ear_value = data.get('ear_value')
    blink_rate = data.get('blink_rate')
    speed = data.get('speed')
    destination = data.get('destination')
    severity = data.get('severity')
    
    # Validasi minimal agar tidak ada data kosong masuk database
    if not driver_id or not event_type:
        return jsonify({"status": "error", "message": "driver_id dan event_type wajib diisi!"}), 400

    try:
        # 3. Simpan log data ke dalam tabel database MySQL (alert_logs)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
            INSERT INTO alert_logs 
            (driver_id, event_type, ear_value, blink_rate, speed, destination, severity, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (driver_id, event_type, ear_value, blink_rate, speed, destination, severity))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "status": "success", 
            "message": f"Data telemetri untuk driver {driver_id} berhasil disimpan 🎉"
        }), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Gagal menyimpan ke database: {str(e)}"}), 500   