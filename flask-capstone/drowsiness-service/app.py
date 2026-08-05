from flask import Flask, Response
import cv2
from datetime import datetime
from pymongo import MongoClient

# Mengimpor modul AI dari folder yang sama
from models.ai_engine import DrowsinessDetector

app = Flask(__name__)

# KONEKSI DATA RIIL: Sambungkan langsung ke MongoDB
MONGO_URI = "mongodb+srv://capstone_db_user:capstone2026@cluster0.k6xslmu.mongodb.net/logisync_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client["logisync_db"]

detector = DrowsinessDetector()
camera = cv2.VideoCapture(0)
     
def generate_frames():
    last_saved_time = datetime.min
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # Proses frame menggunakan ai_engine.py
        frame, data = detector.process_frame(frame)
        
        # JIKA AI MEMICU ALERT (Data Riil Terdeteksi)
        if data["alert_system"]["trigger"]:
            now = datetime.now()
            # Batasi penyimpanan data agar tidak membanjiri DB setiap milidetik (misal: 1 data per 3 detik)
            if (now - last_saved_time).total_seconds() > 3:
                
                # SIMULASI DATA EKSTERNAL: Gabungkan dengan API Cuaca & Speed (atau data statis blackspot)
                # Nantinya nilai ini bisa didapatkan dari HTTP request ke OpenWeather API atau GPS Flutter
                data_eksternal_cuaca = "🌧️ Hujan Lebat" if data["input_metrics"]["waktu_hari"] == "MALAM" else "⛅ Mendung"
                
                # Struktur dokumen Big Data riil yang disimpan ke MongoDB
                telemetry_document = {
                    "driver_name": "Ady Tri",  # Bisa dinamis dari session/token
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "jam": now.strftime("%H:00"), # Untuk grouping grafik Chart.js
                    "status_ai": data["status"],
                    "ear_score": data["ear"],
                    "weather": data_eksternal_cuaca,
                    "speed": 65, # Contoh data kecepatan riil dari kendaraan
                    "is_blackspot": True if data["status"] == "KRITIS" else False # Penanda zona rawan
                }
                
                # Simpan data riil ke MongoDB
                db.trip_telemetry.insert_one(telemetry_document)
                last_saved_time = now
        
        # Konversi ke format JPEG untuk streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Mengembalikan respons JSON (Standar Microservices)
    return {
        "status": "success",
        "service": "Drowsiness AI Service Active",
        "camera_endpoint": "/video_feed",
        "message": "Akses /video_feed di browser untuk melihat stream AI."
    }

if __name__ == '__main__':
    app.run(port=5002, debug=True)