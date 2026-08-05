import sys
import os
import random
import base64
import cv2
import numpy as np
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

MONGO_URI = "mongodb+srv://capstone_db_user:capstone2026@cluster0.k6xslmu.mongodb.net/logisync_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client["logisync_db"]

# Inisialisasi Detektor AI
detector = DrowsinessDetector()

# ==========================================
# 3. FUNGSI BIG DATA (AGREGASI & FILTER WAKTU)
# ==========================================
def get_aggregated_data(time_range="today"):
    sekarang = datetime.now()
    
    # 1. Tentukan batas waktu
    if time_range == "today":
        start_date = sekarang.replace(hour=0, minute=0, second=0, microsecond=0)
        labels = [(sekarang - timedelta(hours=i)).strftime("%H:00") for i in range(4, -1, -1)][::-1]
        is_daily = True
    elif time_range == "7days":
        start_date = sekarang - timedelta(days=7)
        labels = [(sekarang - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)][::-1]
        is_daily = False
    else: # 30days
        start_date = sekarang - timedelta(days=30)
        labels = [(sekarang - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)][::-1]
        is_daily = False
        
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Query manual (jangan gunakan **query_filter agar tidak error)
    # Kita buat query gabungan yang aman
    base_query = {"timestamp": {"$gte": start_date_str}}
    
    # Tambahan query untuk total insiden dan blackspot
    insiden_query = {"status_ai": {"$in": ["MENGANTUK", "KRITIS"]}, "timestamp": {"$gte": start_date_str}}
    blackspot_query = {"is_blackspot": True, "timestamp": {"$gte": start_date_str}}
    
    # 3. Ambil data
    telemetry = list(db.trip_telemetry.find(base_query).sort("_id", -1).limit(20))
    total_insiden = db.trip_telemetry.count_documents(insiden_query)
    total_blackspot = db.trip_telemetry.count_documents(blackspot_query)
    
    all_logs = list(db.trip_telemetry.find(base_query, {"jam": 1, "timestamp": 1, "status_ai": 1, "weather": 1, "is_blackspot": 1}))
    
    # 4. Hitung Counter
    def get_key(log):
        return log.get("jam") if is_daily else log.get("timestamp", "").split(" ")[0]

    int_map = Counter([get_key(log) for log in all_logs if log.get("status_ai") in ["MENGANTUK", "KRITIS"]])
    ext_map = Counter([get_key(log) for log in all_logs if (log.get("is_blackspot") or log.get("weather") in ["Hujan Lebat", "Badai", "Berkabut"])])
    
    return {
        "telemetry": telemetry,
        "chart_labels": labels,
        "chart_internal": [int_map.get(l, 0) for l in labels],
        "chart_external": [ext_map.get(l, 0) for l in labels],
        "total_insiden": total_insiden,
        "total_blackspot": total_blackspot
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
    return render_template('drivers.html', data=get_aggregated_data(), drivers=[])

@app.route('/profile')
def profile_view(): 
    return render_template('profile.html', data=get_aggregated_data(), user={})

@app.route('/login')
def login_view(): 
    return redirect('http://127.0.0.1:5001/login')

@app.route('/scraping-view')
def scraping_view():
    return render_template('scraping.html', data=get_aggregated_data())

if __name__ == '__main__':
    # Debug diset False agar server tidak me-restart otomatis saat demo
    app.run(host='0.0.0.0', port=4000, debug=False)