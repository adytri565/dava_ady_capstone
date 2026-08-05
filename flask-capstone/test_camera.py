# test_camera.py
import cv2
import requests
# Pastikan impor mengarah ke src.models sesuai lokasi barumu
from src.models.ai_engine import DrowsinessDetector

# 🌟 PERBAIKAN UTAMA: Kosongkan kurung di bawah ini!
# Jangan masukkan string "face_landmarker.task" agar path absolut internalnya bekerja.
detector = DrowsinessDetector() 

cap = cv2.VideoCapture(0)

print("Engine AI Aktif. Tekan 'q' untuk keluar...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: 
        break
    
    frame = cv2.flip(frame, 1)
    
    # Jalankan pemrosesan AI wajah
    frame, telemetry = detector.process_frame(frame)
    
    # Kirim data jika terdeteksi mengantuk
    if telemetry["status"] == "Drowsy" or telemetry["status"] == "Drowsiness Detected":
        try:
            payload = {
                "driver_id": "TRK-L412",
                "event_type": "Drowsiness Detected",
                "ear_value": telemetry["ear"],
                "blink_rate": telemetry["blink_rate"],
                "speed": 75,
                "destination": "Semarang Central HUB",
                "severity": "Critical"
            }
            requests.post("http://127.0.0.1:5000/api/detection/report", json=payload, timeout=0.5)
        except requests.exceptions.RequestException:
            pass
            
    cv2.imshow("Driver AI Camera Emulator", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()