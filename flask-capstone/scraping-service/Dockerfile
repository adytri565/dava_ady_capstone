# Menggunakan base image Python resmi yang ringan
FROM python:3.10-slim

# Menetapkan working directory di dalam container
WORKDIR /app

# Menyalin file requirements ke dalam container
COPY requirements.txt .

# Menginstal dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode dalam folder scraping-service ke dalam container
COPY . .

# Mengekspos port Flask (misal port 5003)
EXPOSE 5003

# Menjalankan aplikasi menggunakan Gunicorn atau Python langsung
CMD ["python", "app.py"]