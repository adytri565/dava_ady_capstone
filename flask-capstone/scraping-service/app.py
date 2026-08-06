from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime
from scraper import scrape_data
from preprocessor import clean_text
import os

app = Flask(__name__)

# Koneksi ke MongoDB (Sesuaikan dengan URI database Anda / Docker network)
MONGO_URI = "mongodb://capstone_db_user:capstone2026@ac-4ipoqrj-shard-00-00.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-01.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-02.k6xslmu.mongodb.net:27017/?ssl=true&replicaSet=atlas-x5h8dw-shard-0&authSource=admin&appName=Cluster0"
client = MongoClient(MONGO_URI)
client = MongoClient(MONGO_URI)
db = client["capstone_db"]
collection = db["scraped_data"]

# 1. Rute utama untuk cek status service via browser (Metode GET)
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Scraping Service is running smoothly!"
    }), 200

# 2. Rute utama untuk menjalankan proses scraping (Metode POST)
@app.route('/run-scrape', methods=['POST'])
def run_scraping():
    raw_data = scrape_data()
    inserted_count = 0
    duplicate_count = 0

    for item in raw_data:
        # Preprocessing teks
        item['title'] = clean_text(item['title'])
        item['content'] = clean_text(item['content'])
        
        # Validasi duplikasi berdasarkan 'id' dan 'date'
        query = {
            "id": item['id'],
            "date": item['date']
        }
        
        existing_doc = collection.find_one(query)
        
        if existing_doc:
            # Jika sudah ada, abaikan/skip agar tidak duplikat
            duplicate_count += 1
            continue
        else:
            # Simpan ke MongoDB jika belum ada
            collection.insert_one(item)
            inserted_count += 1

    return jsonify({
        "status": "success",
        "inserted": inserted_count,
        "duplicates_skipped": duplicate_count
    }), 200
# 3. Rute untuk mengambil/menampilkan data hasil scraping (Metode GET)
@app.route('/get-scraped-data', methods=['GET'])
def get_scraped_data():
    try:
        # Mengambil data dari MongoDB, diurutkan dari yang terbaru (limit misal 50 data terakhir)
        data_cursor = collection.find().sort("_id", -1).limit(50)
        
        scraped_list = []
        for doc in data_cursor:
            scraped_list.append({
                "id": doc.get("id", "-"),
                "title": doc.get("title", "-"),
                "content": doc.get("content", "-"),
                "date": doc.get("date", "-")
            })
            
        return jsonify({
            "status": "success",
            "count": len(scraped_list),
            "data": scraped_list
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)