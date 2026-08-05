import re

def clean_text(text):
    if not text:
        return ""
    # Mengubah ke huruf kecil
    text = text.lower()
    # Menghapus karakter khusus, angka, dan tanda baca yang tidak penting
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Menghapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    return text