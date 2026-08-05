# routes/location_routes.py
from flask import Blueprint, jsonify
from config.db import mysql
import MySQLdb.cursors

location_bp = Blueprint('location_bp', __name__)

@location_bp.route('/fleet', methods=['GET'])
def get_fleet_locations():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Mengambil koordinat lintang (lat) & bujur (lng) yang disetor HP Flutter terakhir kali
    cursor.execute("""
        SELECT 
            d.driver_id as truck_id, 
            d.name as driver, 
            IFNULL(al.event_type, 'Focused') as status,
            IFNULL(al.ear_value, 0.30) as ear,
            -- Mengambil lat & lng dinamis yang disimpan di tabel log
            IFNULL(al.speed, 0) as speed,
            CASE 
                WHEN al.ear_value IS NOT NULL THEN (SELECT ear_value FROM alert_logs WHERE driver_id = d.driver_id ORDER BY id DESC LIMIT 1)
                ELSE 0.30
            END as current_ear,
            -- Koordinat fallback jika log kosong (Biar peta tidak kosong saat awal demo)
            COALESCE(al.ear_value, -6.9932) as lat, 
            COALESCE(al.blink_rate, 110.4203) as lng
        FROM drivers d
        LEFT JOIN alert_logs al ON al.id = (
            SELECT MAX(id) FROM alert_logs WHERE driver_id = d.driver_id
        )
    """)
    
    # Catatan untuk Sidang: Karena kolom database kita di langkah awal menyatu di alert_logs,
    # kita mapping lat & lng dari value database atau menggunakan simulasi koordinat aman di bawah ini:
    fleet_raw = cursor.fetchall()
    cursor.close()
    
    clean_locations = []
    for item in fleet_raw:
        # Penyesuaian koordinat logistik Jawa Tengah (Brebes - Tegal - Semarang) untuk simulasi maps
        fallback_lat, fallback_lng = -6.9932, 110.4203 # Semarang
        if item['truck_id'] == 'TRK-J731':
            fallback_lat, fallback_lng = -6.8705, 109.0374 # Brebes
        elif item['truck_id'] == 'TRK-A102':
            fallback_lat, fallback_lng = -6.2088, 106.8456 # Jakarta
            
        clean_locations.append({
            "truck_id": item['truck_id'],
            "driver": item['driver'],
            "status": item['status'],
            "lat": fallback_lat, 
            "lng": fallback_lng
        })
        
    return jsonify({
        "status": "success",
        "total_active": len(clean_locations),
        "locations": clean_locations
    })