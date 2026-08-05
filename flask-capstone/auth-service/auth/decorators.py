# Gambaran umum cara decorators.py kamu membaca JWT dari Flutter:
auth_header = request.headers.get('Authorization')
if auth_header:
    token = auth_header.split(" ")[1] # Mengambil string token setelah kata 'Bearer'
    # Lalu didecode menggunakan jwt_utils...