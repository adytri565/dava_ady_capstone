from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from collections import Counter

app = Flask(__name__)

# 1. KONEKSI MONGODB ATLAS
MONGO_URI = "mongodb://capstone_db_user:capstone2026@ac-4ipoqrj-shard-00-00.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-01.k6xslmu.mongodb.net:27017,ac-4ipoqrj-shard-00-02.k6xslmu.mongodb.net:27017/?ssl=true&replicaSet=atlas-x5h8dw-shard-0&authSource=admin&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["logisync_db"]
collection = db["scraped_news"] 

# 2. FUNGSI PREPROCESSING (TEXT CLEANING & STOPWORD REMOVAL)
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    stopwords = ['di', 'ke', 'dari', 'yang', 'dan', 'atau', 'untuk', 'ini', 'itu', 'dengan', 'pada', 'dalam', 'news', 'com', 'id']
    words = text.split()
    cleaned_words = [w for w in words if w not in stopwords]
    return " ".join(cleaned_words)

# 3. FUNGSI CRAWLING, VALIDASI DUPLIKAT, & SIMPAN KE DB
def run_automated_scraping():
    print(f"\n[{datetime.now()}] Memulai proses scraping otomatis...")
    search_query = "cuaca+OR+lalu+lintas+OR+logistik+OR+pantura"
    url = f"https://news.google.com/rss/search?q={search_query}&hl=id&gl=ID&ceid=ID:id"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        saved_count = 0
        duplicate_count = 0
        
        for item in items:
            raw_title = item.title.text if item.title else "Tanpa Judul"
            
            # Validasi Duplikat Berdasarkan Judul di MongoDB
            is_duplicate = collection.find_one({"title": raw_title})
            if is_duplicate:
                duplicate_count += 1
                continue # Lewati jika sudah ada agar tidak duplikat
            
            raw_content = item.description.text if item.description else "-"
            clean_html = BeautifulSoup(raw_content, "html.parser").get_text(strip=True)
            
            cleaned_title = clean_text(raw_title)
            cleaned_content = clean_text(clean_html)
            
            doc = {
                "id": f"SCR-{str(uuid.uuid4())[:6].upper()}",
                "title": raw_title,
                "title_cleaned": cleaned_title,
                "content_cleaned": cleaned_content,
                "date": item.pubDate.text if item.pubDate else datetime.utcnow().strftime('%Y-%m-%d'),
                "scraped_at": datetime.now()
            }
            collection.insert_one(doc)
            saved_count += 1
            
        print(f"Scraping Selesai! Tersimpan: {saved_count} berita baru. Duplikat dilewati: {duplicate_count}")
        return {"status": "success", "saved": saved_count, "duplicates": duplicate_count}
        
    except Exception as e:
        print(f"Error scraping: {e}")
        return {"status": "error", "message": str(e)}

# 4. SCHEDULING (AUTOMATISASI BACKGROUND)
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_automated_scraping, trigger="interval", hours=1, id="scrape_job", replace_existing=True)
scheduler.start()

# 5. ROUTES API UTAMA
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "success", "message": "Scraping Service is running smoothly!"})

@app.route('/run-scrape', methods=['GET', 'POST'])
def manual_scrape():
    result = run_automated_scraping()
    return jsonify(result)

@app.route('/get-scraped-data', methods=['GET'])
def get_scraped_data():
    data_from_db = list(collection.find({}, {"_id": 0}).sort("scraped_at", -1).limit(20))
    return jsonify({"count": len(data_from_db), "data": data_from_db, "status": "success"})

@app.route('/analyze-words', methods=['GET'])
def analyze_words():
    try:
        docs = list(collection.find({}, {"title_cleaned": 1, "content_cleaned": 1, "_id": 0}))
        all_words = []
        for doc in docs:
            text = f"{doc.get('title_cleaned', '')} {doc.get('content_cleaned', '')}"
            all_words.extend(text.split())
        
        word_counts = Counter(all_words)
        top_10_words = word_counts.most_common(10)
        
        labels = [item[0] for item in top_10_words]
        values = [item[1] for item in top_10_words]
        
        return jsonify({"labels": labels, "values": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-schedule', methods=['POST'])
def update_schedule():
    data = request.json
    hours = int(data.get('hours', 1))
    try:
        scheduler.reschedule_job('scrape_job', trigger='interval', hours=hours)
        return jsonify({"status": "success", "message": f"Otomatisasi diubah ke {hours} jam"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    run_automated_scraping() 
    app.run(host='0.0.0.0', port=5003, debug=False)