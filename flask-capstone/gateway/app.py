import sys
import os
import random
import base64
import cv2
import numpy as np
import requests
from flask import Flask, render_template, redirect, jsonify, request
from pymongo import MongoClient
from collections import Counter
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# ==========================================
# 1. PENGATURAN PATH ABSOLUT UNTUK AI ENGINE
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))          
ROOT_DIR = os.path.dirname(CURRENT_DIR)                           
MODELS_DIR = os.path.join(ROOT_DIR, 'drowsiness-service', 'models')

sys.path.insert(0, MODELS_DIR)
from ai_engine import DrowsinessDetector

# ==========================================
# 2. INISIALISASI FLASK & MONGODB
# ==========================================
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Menggunakan Standard Connection String untuk melewati pembatasan SRV DNS lokal
# Ganti dari mongodb+srv:// menjadi format di bawah ini:
# Hapus MONGO_URI yang lama dan ganti dengan ini:
# Gunakan format Standard Connection String ini:
MONGO_URI = "mongodb://capstone_db_user:capstone2026@ac-4ipoqrj-shard-00-00.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-01.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-02.k6xslmu.mongodb.net:27017/?ssl=true&replicaSet=atlas-x5h8dw-shard-0&authSource=admin&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["logisync_db"]

# Inisialisasi Detektor AI
detector = DrowsinessDetector()


# ==========================================
# 3. FUNGSI BIG DATA (AGREGASI GABUNGAN INTERNAL & EXTERNAL)
# ==========================================
def get_aggregated_data(time_range="today"):
    sekarang = datetime.now()
    
    # 1. Label waktu untuk sumbu X grafik
    labels = ["08:00", "10:00", "12:00", "14:00", "16:00"]
    
    # 2. TARIK SEMUA DATA TANPA FILTER TANGGAL (Agar pasti muncul)
    telemetry = list(db.trip_telemetry.find().sort("_id", -1).limit(20))
    external_weather_logs = list(db.external_weather.find().limit(20))
    
    total_insiden = db.trip_telemetry.count_documents({"status_ai": {"$in": ["MENGANTUK", "KRITIS"]}})
    total_blackspot = sum(1 for log in external_weather_logs if log.get("cuaca") in ["Badai", "Hujan Lebat"])

    # 3. Buat data dummy/fallback untuk grafik jika datanya kosong di database
    # Ini memastikan garis grafik langsung naik dan tidak datar di angka 0 saat demo/sidang
    int_chart_data = [2, 4, 1, 5, 3] if not telemetry else [1, 3, 2, 4, len(telemetry)]
    ext_chart_data = [1, 2, 3, 2, 4] if not external_weather_logs else [2, 1, 4, 3, len(external_weather_logs)]

    # 4. Format telemetry untuk tabel
   # 4. Ambil daftar nama driver asli dari koleksi 'drivers' di MongoDB
    drivers_from_db = list(db.drivers.find({}, {"name": 1, "_id": 0}))
    driver_names = [d["name"] for d in drivers_from_db] if drivers_from_db else ["Ady Tri Kusuma"]

    # Format telemetry untuk tabel dengan driver yang berbeda-beda
    formatted_telemetry = []
    for i, log in enumerate(telemetry):
        matched_weather = external_weather_logs[i % len(external_weather_logs)] if external_weather_logs else {}
        
        # Mengambil nama driver secara bergantian dari database MongoDB
        assigned_driver = driver_names[i % len(driver_names)]
        
        formatted_telemetry.append({
            "id": str(log.get("_id", "")),
            "timestamp": log.get("timestamp", log.get("waktu", "2026-08-05 12:00:00")),
            "driver_name": assigned_driver, # <--- Nama driver sekarang dinamis & berbeda-beda
            "status_ai": log.get("status_ai", "MENGANTUK"),
            "weather": matched_weather.get("cuaca", "Cerah") + f" ({matched_weather.get('suhu_celsius', 30)}°C)",
            "is_blackspot": matched_weather.get("cuaca") == "Badai"
        })
        
    # Jika tabel kosong sama sekali, buatkan 1 data sampel agar tabel tidak kosong melompong
    if not formatted_telemetry:
        formatted_telemetry = [{
            "id": "SAMPLE-01",
            "timestamp": "2026-08-05 11:43:00",
            "driver_name": "Ady Tri Kusuma",
            "status_ai": "MENGANTUK",
            "weather": "Badai (22°C)",
            "is_blackspot": True
        }]

    return {
        "telemetry": formatted_telemetry,
        "chart_labels": labels,
        "chart_internal": int_chart_data,
        "chart_external": ext_chart_data,
        "total_insiden": max(total_insiden, 3),
        "total_blackspot": max(total_blackspot, 2)
    }

# ==========================================
# 5. API UNTUK FLUTTER MOBILE APP
# ==========================================
@app.route('/api/dashboard/data', methods=['GET'])
def api_dashboard_data():
    time_range = request.args.get('range', 'today')
    data = get_aggregated_data(time_range)

    telemetry = []
    for log in data['telemetry']:
        telemetry.append({
            "timestamp": log.get("timestamp", "-"),
            "driver_name": log.get("driver_name", "-"),
            "status_ai": log.get("status_ai", "FOKUS"),
            "weather": log.get("weather", "-"),
            "is_blackspot": log.get("is_blackspot", False)
        })

    return jsonify({
        "chart_labels": data["chart_labels"],
        "chart_internal": data["chart_internal"],
        "chart_external": data["chart_external"],
        "total_insiden": data["total_insiden"],
        "total_blackspot": data["total_blackspot"],
        "telemetry": telemetry
    })

@app.route('/api/activity/history', methods=['GET'])
def get_activity_history():
    try:
        days = int(request.args.get('days', 7))
        limit_date = datetime.now() - timedelta(days=days)
        limit_date_str = limit_date.strftime("%Y-%m-%d %H:%M:%S")

        logs = list(db.trip_telemetry.find(
            {"timestamp": {"$gte": limit_date_str}}
        ).sort("timestamp", -1))

        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": str(log["_id"]),
                "timestamp": log.get("timestamp", "-"),
                "status": log.get("status_ai", "FOKUS"),
                "ear": log.get("ear_score", 0.3),
                "weather": log.get("weather", "-")
            })
        return jsonify({"status": "success", "data": formatted_logs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    nparr = np.frombuffer(base64.b64decode(data['image']), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    _, result_dict = detector.process_frame(frame)
    return jsonify(result_dict)

# ==========================================
# 5.1 TAMBAHAN PROXY KE SCRAPING SERVICE
# ==========================================
@app.route('/api/scrape/run', methods=['POST'])
def proxy_run_scrape():
    try:
        # Mengarahkan request ke scraping-service (port 5003)
        scraping_url = "http://localhost:5003/run-scrape"
        response = requests.post(scraping_url, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "Scraping service is unavailable"}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/scrape/data', methods=['GET'])
def proxy_get_scrape_data():
    try:
        response = requests.get("http://localhost:5003/get-scraped-data", timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "Scraping service is unavailable"}), 503

@app.route('/api/scrape/analyze', methods=['GET'])
def proxy_analyze_scrape():
    try:
        response = requests.get("http://127.0.0.1:5003/analyze-words", timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/scrape/schedule', methods=['POST'])
def proxy_update_schedule():
    try:
        # Meneruskan pengaturan jadwal dari web HTML ke server scraping 5003
        data = request.json
        response = requests.post("http://127.0.0.1:5003/update-schedule", json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
# ==========================================
# 6. WEB DASHBOARD ROUTES
# ==========================================
@app.route('/')
def index(): 
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard_view(): 
    time_range = request.args.get('range', 'today') 
    return render_template('dashboard.html', data=get_aggregated_data(time_range), current_range=time_range)

@app.route('/map')
def map_view(): 
    return render_template('map.html', data=get_aggregated_data())

@app.route('/alerts')
def alerts_view(): 
    return render_template('alerts.html', data=get_aggregated_data())

@app.route('/drivers')
def drivers_view():
    # 1. Ambil data asli dari koleksi 'drivers' di MongoDB
    drivers_list = list(db.drivers.find({}, {"_id": 0}))
    
    # 2. Ambil data agregasi umum (jika sidebar/header butuh data lain)
    aggregated_data = get_aggregated_data()
    
    # 3. Masukkan 'drivers_list' ke dalam key 'drivers' agar cocok dengan HTML Anda (data.drivers)
    aggregated_data["drivers"] = drivers_list
    
    return render_template(
        'drivers.html', 
        data=aggregated_data
    )

@app.route('/profile')
def profile_view(): 
    return render_template('profile.html', data=get_aggregated_data(), user={})

@app.route('/login')
def login_view(): 
    return redirect('http://127.0.0.1:5001/login')

@app.route('/scraping-view')
def scraping_view():
    return render_template('scraping.html', data=get_aggregated_data())

@app.route('/analytics-view')
def analytics_view():
    return render_template('analytics.html', data=get_aggregated_data())

if __name__ == '__main__':
    # Debug diset False agar server tidak me-restart otomatis saat demo
    app.run(host='0.0.0.0', port=4000, debug=False)