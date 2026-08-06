import re
from pymongo import MongoClient

# Contoh daftar stopword sederhana bahasa Indonesia (atau gunakan Sastrawi/NLTK)
STOPWORDS = set(['dan', 'yang', 'di', 'dari', 'ke', 'ini', 'itu', 'untuk', 'pada', 'adalah', 'dengan'])

def clean_text(text):
    if not text:
        return ""
    # Menghapus karakter khusus / simbol, ubah ke lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
    # Stopword removal sederhana
    words = text.split()
    filtered_words = [word for word in words if word not in STOPWORDS]
    return " ".join(filtered_words)

def process_and_save_data(scraped_items, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client['dava_capstone_db'] # Sesuaikan nama database Anda
    collection = db['news_collection'] # Sesuaikan nama collection Anda
    
    saved_count = 0
    for item in scraped_items:
        # 4. Preprocessing: Cek apakah ada data yang null/kosong
        if not item.get('id') or not item.get('title') or not item.get('content'):
            continue # Lewati jika ada data penting yang null
            
        # Preprocessing teks (Stopword removal & cleaning)
        item['clean_content'] = clean_text(item['content'])
        
        # 2. Validasi Duplikat (By ID atau By Date/URL)
        existing_item = collection.find_one({
            "$or": [
                {"id": item['id']},
                {"url": item.get('url')}
            ]
        })
        
        if existing_item:
            # Jika sudah ada, Anda bisa memilih untuk mengabaikannya atau menghapusnya
            # Sesuai ketentuan soal: "kalau duplikat akan dihapus / tidak dimasukkan"
            continue
        else:
            # Simpan data baru yang sudah bersih ke MongoDB
            collection.insert_one(item)
            saved_count += 1
            
    print(f"Berhasil menyimpan {saved_count} data baru yang unik dan bersih.")