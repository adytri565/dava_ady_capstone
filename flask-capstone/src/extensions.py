from pymongo import MongoClient

# Konfigurasi koneksi (Bisa dipindahkan ke .env nanti)
MONGO_URI = "mongodb+srv://capstone_db_user:capstone2026@cluster0.k6xslmu.mongodb.net/logisync_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

# Inisialisasi client
client = MongoClient(MONGO_URI)
db = client["logisync_db"] # Database utama Anda