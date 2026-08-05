# src/models/ai_engine.py
import cv2
import numpy as np
import time
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 🌟 KUNCI ABSOLUT: Mengambil lokasi folder src/models secara dinamis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE_PATH = os.path.join(BASE_DIR, "face_landmarker.task")

class DrowsinessDetector:
    def __init__(self, model_path=MODEL_FILE_PATH):
        # Inisialisasi MediaPipe Tasks Face Landmarker menggunakan path absolut
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Threshold Parameter Biometrik
        self.EAR_THRESHOLD = 0.21        
        self.YAWN_THRESHOLD = 25.0       
        
        # Variabel State Real-time (Mata & Blink)
        self.eye_state_closed = False
        self.blink_counter = 0
        self.blink_rate_per_minute = 0
        self.start_time = time.time()
        
        # ⏱️ Variabel Baru: Tracking Waktu Real-Time untuk Detik
        self.eye_closed_start_time = None  # Menyimpan timestamp saat mata mulai tertutup
        self.drive_start_time = time.time() # Menghitung durasi berkendara sejak apps dinyalakan

    def calculate_distance(self, p1, p2, w, h):
        x1, y1 = p1.x * w, p1.y * h
        x2, y2 = p2.x * w, p2.y * h
        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def calculate_ear(self, landmarks, eye_indices, w, h):
        p1 = landmarks[eye_indices[0]]
        p2 = landmarks[eye_indices[1]]
        p3 = landmarks[eye_indices[2]]
        p4 = landmarks[eye_indices[3]]
        p5 = landmarks[eye_indices[4]]
        p6 = landmarks[eye_indices[5]]

        v1 = self.calculate_distance(p2, p6, w, h)
        v2 = self.calculate_distance(p3, p5, w, h)
        h_dist = self.calculate_distance(p1, p4, w, h)

        return (v1 + v2) / (2.0 * h_dist)

    def estimate_head_pose(self, landmarks):
        """
        Mengestimasi kemiringan kepala (menunduk) secara sederhana memanfaatkan koordinat Z 
        atau perbandingan jarak vertikal hidung-dagu/dahi.
        """
        # Landmark hidung (1), dagu (152), dahi atas (10)
        nose = landmarks[1]
        chin = landmarks[152]
        forehead = landmarks[10]
        
        # Menggunakan rasio jarak atau nilai kedalaman Z untuk mendeteksi kepala menunduk
        # Jika kepala menunduk, jarak dahi ke hidung secara visual memendek, atau nilai Z dahi berubah signifikan.
        # Logika sederhana: perbandingan posisi Y relatif
        upper_face = abs(nose.y - forehead.y)
        lower_face = abs(chin.y - nose.y)
        
        # Jika lower_face jauh lebih kecil dibanding upper_face, indikasi kepala menunduk (pitch ke bawah)
        if lower_face < (upper_face * 0.75): 
            return "MENUNDUK"
        return "NORMAL"

    def get_time_of_day(self):
        """Mendapatkan info waktu saat ini (Siang / Malam)"""
        current_hour = time.localtime().tm_hour
        if 6 <= current_hour < 18:
            return "SIANG"
        else:
            return "MALAM"

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        result = self.detector.detect(mp_image)
        
        # Default State Input
        status_mata = "open"
        kepala_pose = "NORMAL"
        durasi_mata_tertutup = 0.0
        durasi_berkendara = (time.time() - self.drive_start_time) / 60.0 # dalam menit
        waktu_sekarang = self.get_time_of_day()
        
        status_ai = "NORMAL"
        trigger_alert = False
        alert_type = []
        
        ear_avg = 0.28
        
        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            
            # 1. Hitung EAR (Eye Aspect Ratio)
            left_eye_idx = [33, 160, 158, 133, 153, 144]
            right_eye_idx = [362, 385, 387, 263, 373, 380]
            
            ear_left = self.calculate_ear(landmarks, left_eye_idx, w, h)
            ear_right = self.calculate_ear(landmarks, right_eye_idx, w, h)
            ear_avg = float(round((ear_left + ear_right) / 2.0, 2))
            
            # 2. Estimasi Head Pose
            kepala_pose = self.estimate_head_pose(landmarks)
            
            # 3. Logika Durasi Mata Tertutup (Berbasis Waktu Nyata / Detik)
            if ear_avg < self.EAR_THRESHOLD:
                status_mata = "closed"
                if self.eye_closed_start_time is None:
                    self.eye_closed_start_time = time.time() # Mulai hitung detik
                else:
                    durasi_mata_tertutup = time.time() - self.eye_closed_start_time
                
                if not self.eye_state_closed:
                    self.eye_state_closed = True
            else:
                status_mata = "open"
                if self.eye_state_closed:
                    self.blink_counter += 1
                    self.eye_state_closed = False
                self.eye_closed_start_time = None # Reset tracker waktu
                durasi_mata_tertutup = 0.0

            # 4. Hitung Blink Rate per Menit
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 60:
                self.blink_rate_per_minute = self.blink_counter
                self.blink_counter = 0
                self.start_time = time.time()
            else:
                self.blink_rate_per_minute = int(self.blink_counter * (60 / max(elapsed_time, 1)))

            # 5. 🧠 RULE-BASED LOGIC (Sesuai Spesifikasi Permintaan)
            # Kondisi KRITIS: Mata tertutup > 2 detik AND kepala menunduk
            if durasi_mata_tertutup > 2.0 and kepala_pose == "MENUNDUK":
                status_ai = "KRITIS"
                trigger_alert = True
                alert_type = ["SUARA ALARM", "POPUP VISUAL", "VIBRATION"] # Respon maksimal
                
            # Kondisi MENGANTUK: Mata tertutup > 2 detik ATAU kepala menunduk
            elif durasi_mata_tertutup > 2.0:
                status_ai = "MENGANTUK"
                trigger_alert = True
                alert_type = ["SUARA ALARM", "POPUP VISUAL"]
                
            elif kepala_pose == "MENUNDUK":
                status_ai = "MENGANTUK"
                trigger_alert = True
                alert_type = ["POPUP VISUAL", "VIBRATION"]
                
            # Tambahan faktor kelelahan ekstra (Contoh: berkendara > 120 menit atau malam hari)
            elif durasi_berkendara > 120.0 or waktu_sekarang == "MALAM":
                # Jika indikasi mata mulai sayu (sedikit di bawah normal tapi belum merem total)
                if ear_avg < (self.EAR_THRESHOLD + 0.03): 
                    status_ai = "WASPADA (LELAH)"
                    trigger_alert = True
                    alert_type = ["POPUP VISUAL"]
            else:
                status_ai = "FOCUSED"

            # 6. Menggambar Informasi GUI / Overlay Video
            # Mengubah warna teks berdasarkan tingkat keparahan
            if status_ai == "KRITIS":
                color = (0, 0, 255) # Merah benderang
            elif status_ai == "MENGANTUK":
                color = (0, 61, 255) # Oranye / Kuning Tua
            else:
                color = (0, 230, 118) # Hijau jika normal
                
            cv2.putText(frame, f"STATUS: {status_ai}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, f"Mata Tertutup: {durasi_mata_tertutup:.1f}s", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Pose Kepala: {kepala_pose}", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Waktu: {waktu_sekarang} | Durasi: {durasi_berkendara:.1f}m", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Popup Visual sederhana di layar jika alert aktif
            if trigger_alert:
                cv2.rectangle(frame, (15, 15), (w - 15, h - 15), color, 4) # Bingkai Alert Berkedip
                cv2.putText(frame, "!!! PERINGATAN !!!", (w // 2 - 100, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return frame, {
            "status": status_ai,
            "ear": ear_avg,
            "blink_rate": self.blink_rate_per_minute,
            "input_metrics": {
                "status_mata": status_mata,
                "head_pose": kepala_pose,
                "durasi_tertutup": round(durasi_mata_tertutup, 2),
                "durasi_berkendara_menit": round(durasi_berkendara, 2),
                "waktu_hari": waktu_sekarang
            },
            "alert_system": {
                "trigger": trigger_alert,
                "actions": alert_type
            }
        }