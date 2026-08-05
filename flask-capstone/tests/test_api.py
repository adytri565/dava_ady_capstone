import pytest
import requests
import json

# URL Gateway atau Auth Service Anda
BASE_URL = "http://127.0.0.1:5001" 

# Fungsi untuk generate 30 data dummy
def get_dummy_users():
    users = []
    for i in range(30):
        users.append({
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "password": "password123"
        })
    return users

# Test Case 1: Testing Registrasi 30 User (Data Driven)
@pytest.mark.parametrize("user_data", get_dummy_users())
def test_register_user(user_data):
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    # Kita berekspektasi status 201 (Created) atau 400 (karena sudah ada)
    assert response.status_code in [201, 400]

# Test Case 2: Testing Login
def test_login_user():
    user = {"email": "user0@example.com", "password": "password123"}
    response = requests.post(f"{BASE_URL}/login", json=user)
    assert response.status_code == 200
    assert "token" in response.json()

# Test Case 3: Testing Akses Tanpa Token (Security Test)

def test_access_without_token():
    # Akses tanpa token SEHARUSNYA menghasilkan 401 Unauthorized
    response = requests.get("http://127.0.0.1:5002/drivers")
    assert response.status_code == 401