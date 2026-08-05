import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_data():
    # Sesuaikan URL target sesuai hasil Inspect HTML project Anda
    url = "https://example.com/target-data" 
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Gagal mengambil data")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    scraped_data = []

    # Contoh parsing elemen HTML (sesuaikan dengan target Anda)
    items = soup.find_all('div', class_='data-item')
    for item in items:
        data_id = item.get('data-id', 'unknown_id')
        title = item.find('h2').get_text(strip=True)
        content = item.find('p').get_text(strip=True)
        
        scraped_data.append({
            "id": data_id,
            "title": title,
            "content": content,
            "date": datetime.utcnow().strftime('%Y-%m-%d')
        })
        
    return scraped_data