from app import run_automated_scraping

if __name__ == "__main__":
    print("Memulai proses scraping terjadwal via GitHub Actions...")
    result = run_automated_scraping()
    print("Hasil Scraping:", result)