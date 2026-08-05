import json
from datetime import datetime

# Sesuaikan path file JSON Anda
file_path = "scraping-service/data.json"

# 1. Baca data yang sudah ada di file JSON
try:
    with open(file_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

# 2. Buat data baru secara dinamis berdasarkan waktu saat ini
current_time = datetime.now()
new_entry = {
    "id": f"item_{int(current_time.timestamp())}",
    "title": f"Update Otomatis Sistem Logistik - {current_time.strftime('%H:%M')}",
    "content": f"Data telemetri dan pemantauan diperbarui secara otomatis pada tanggal {current_time.strftime('%Y-%m-%d %H:%M:%S')}.",
    "date": current_time.strftime('%Y-%m-%d')
}

# 3. Masukkan data baru ke dalam list
data.append(new_entry)

# 4. Simpan kembali ke file JSON
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)

print("Data berhasil diperbarui secara otomatis!")