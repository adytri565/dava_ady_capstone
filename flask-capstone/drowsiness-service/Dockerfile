# 1. Gunakan base image yang ringan
FROM python:3.9-slim

# 2. Set working directory di dalam container
WORKDIR /app

# 3. Install dependencies system (Penting untuk OpenCV agar bisa jalan di Linux)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy file requirements.txt terlebih dahulu (agar caching optimal)
COPY requirements.txt .

# 5. Install dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh source code ke dalam container
COPY . .

# 7. Expose port yang digunakan Flask
EXPOSE 5000

# 8. Perintah untuk menjalankan aplikasi
CMD ["python", "app.py"]