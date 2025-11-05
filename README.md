# KUWAMEDYA - Dijital Ajans Web Sitesi

Modern ve kapsamlı bir dijital ajans web sitesi. Flask tabanlı, tam özellikli bir yönetim paneli ve akademi sistemi içerir.

## 🚀 Özellikler

- **Vitrin Web Sitesi**: Portfolyo, hizmet paketleri, ekip tanıtımı
- **Admin Paneli**: Kurs, proje, personel ve paket yönetimi
- **Akademi Sistemi**: Online kurslar, dersler ve quizler
- **Sertifika Sistemi**: PDF sertifika oluşturma ve indirme
- **Tema Desteği**: Açık/koyu mod desteği
- **Responsive Tasarım**: Mobil uyumlu modern arayüz

## 📋 Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)
- PostgreSQL (Production için) veya SQLite (Development için)

## 🛠️ Kurulum

### 1. Projeyi İndirin

```bash
git clone https://github.com/kullanici/kuwamedya.git
cd kuwamedya
```

### 2. Sanal Ortam Oluşturun

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarlayın

```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin ve kendi değerlerinizi girin
# ÖNEMLİ: SECRET_KEY'i mutlaka değiştirin!
```

**.env dosyasında düzenlemeniz gerekenler:**

```env
FLASK_ENV=dev
SECRET_KEY=your-secret-key-here  # python -c "import secrets; print(secrets.token_hex(32))" ile oluşturun
DEV_DATABASE_URL=sqlite:///instance/kuwamedyadb-dev.db
```

### 5. Veritabanını Oluşturun

```bash
# Veritabanı tablolarını oluştur
flask db upgrade

# Veya migration yoksa:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Veritabanını Doldurun (Örnek Veriler)

```bash
flask seed
```

Bu komut:
- Admin kullanıcısı oluşturur
- Örnek kurslar, dersler ve quizler ekler
- Örnek projeler ve personel ekler

**Varsayılan Admin Bilgileri:**
- Kullanıcı Adı: `admin`
- E-posta: `admin@kuwamedya.com`
- Şifre: `Kuwamedya2025!Admin` (İlk girişten sonra mutlaka değiştirin!)

### 7. Uygulamayı Başlatın

```bash
flask run
```

Tarayıcınızda `http://127.0.0.1:5000` adresine gidin.

## 🔒 Güvenlik

### Production Ortamı İçin Önemli Ayarlar

1. **SECRET_KEY'i Değiştirin:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Çıktıyı `.env` dosyasındaki `SECRET_KEY` değeri olarak kullanın.

2. **Veritabanı Güvenliği:**
   - Production için mutlaka PostgreSQL veya MySQL kullanın
   - SQLite sadece development için uygundur
   - Veritabanı şifrelerini güvenli tutun

3. **HTTPS Kullanın:**
   - Production ortamında mutlaka HTTPS aktif olmalı
   - `SESSION_COOKIE_SECURE = True` ayarı zaten yapılmış

4. **Admin Şifresini Değiştirin:**
   - İlk girişten sonra admin şifresini mutlaka değiştirin
   - Güçlü bir şifre kullanın (en az 12 karakter, büyük/küçük harf, sayı, özel karakter)

## 📁 Proje Yapısı

```
kuwamedya/
├── app.py                 # Ana uygulama dosyası
├── config.py             # Yapılandırma ayarları
├── models.py             # Veritabanı modelleri
├── forms.py              # WTForms form tanımları
├── seed.py               # Veritabanı seed komutu
├── requirements.txt      # Python bağımlılıkları
├── .env.example          # Ortam değişkenleri örneği
├── migrations/           # Alembic veritabanı migration'ları
├── static/              # Statik dosyalar (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # Jinja2 şablonları
│   ├── admin/          # Admin panel şablonları
│   ├── panel/         # Kullanıcı paneli şablonları
│   └── ...
└── instance/          # Veritabanı dosyaları (gitignore'da)
```

## 🔧 Yapılandırma

### Development (Geliştirme)

```env
FLASK_ENV=dev
DEBUG=True
```

### Production (Canlı)

```env
FLASK_ENV=prod
DEBUG=False
DATABASE_URL=postgresql://kullanici:sifre@localhost/kuwamedya_db
```

## 📝 Kullanılabilir Komutlar

```bash
# Veritabanı migration oluştur
flask db migrate -m "Açıklama"

# Veritabanı migration uygula
flask db upgrade

# Veritabanını sıfırla ve örnek verilerle doldur
flask seed

# Admin kullanıcı oluştur
flask create-admin "İsim" "kullanici_adi" "email@example.com" "sifre"
```

## 🌐 Production Deployment

### 1. Sunucu Gereksinimleri

- Python 3.8+
- PostgreSQL veya MySQL
- Nginx (reverse proxy için)
- Gunicorn veya uWSGI (WSGI server)

### 2. Adımlar

1. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install gunicorn
   ```

2. **Ortam Değişkenlerini Ayarlayın:**
   ```bash
   export FLASK_ENV=prod
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=postgresql://...
   ```

3. **Veritabanını Oluşturun:**
   ```bash
   flask db upgrade
   flask seed  # İsterseniz
   ```

4. **Gunicorn ile Çalıştırın:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
   ```

5. **Nginx Yapılandırması:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🐛 Sorun Giderme

### Veritabanı Hatası

```bash
# Veritabanını sıfırlamak için
rm instance/kuwamedyadb-dev.db
flask db upgrade
flask seed
```

### Port Zaten Kullanılıyor

```bash
# Farklı bir port kullanın
flask run --port 5001
```

## 📄 Lisans

Bu proje özel bir projedir. Tüm hakları saklıdır.

## 👤 İletişim

Sorularınız için: [Email adresiniz]

---

**Not:** Bu proje production için hazırlanmıştır. Deploy etmeden önce güvenlik ayarlarını kontrol ettiğinizden emin olun.

