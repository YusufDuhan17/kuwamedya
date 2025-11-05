import requests
import json

# API sunucumuzun adresi
API_URL = 'http://127.0.0.1:5000/calculate'

# API'ya göndereceğimiz veri (payload)
# Yusuf Şahin (user_id=1) için Ekim 2025 (year=2025, month=10) primini hesapla
payload = {
    'user_id': 1,
    'year': 2025,
    'month': 10
}

# POST isteğini gönderiyoruz
try:
    response = requests.post(API_URL, json=payload)
    
    # Sunucudan gelen cevabı ekrana yazdır
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

except requests.exceptions.ConnectionError as e:
    print("\nHATA: Sunucuya bağlanılamadı.")
    print("Lütfen 'flask run' komutunu çalıştırdığınızdan emin olun.")