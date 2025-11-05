# 🚀 KUWAMEDYA - Production Deployment Kılavuzu

Bu dosya, KUWAMEDYA projesini production ortamına deploy etmek için adım adım talimatlar içerir.

## 📋 Ön Hazırlık

### 1. Sunucu Gereksinimleri

- **İşletim Sistemi**: Ubuntu 20.04+ veya CentOS 7+
- **Python**: 3.8 veya üzeri
- **Veritabanı**: PostgreSQL 12+ (önerilen) veya MySQL 8+
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Domain**: SSL sertifikası ile (Let's Encrypt önerilir)

### 2. Sunucuya Bağlanma

```bash
ssh kullanici@sunucu-ip-adresi
```

## 🔧 Adım 1: Sunucu Kurulumu

### Python ve Gerekli Paketler

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server nginx git
```

### PostgreSQL Kurulumu ve Veritabanı Oluşturma

```bash
# PostgreSQL servisini başlat
sudo systemctl start postgresql
sudo systemctl enable postgresql

# PostgreSQL'e bağlan
sudo -u postgres psql

# Veritabanı ve kullanıcı oluştur
CREATE DATABASE kuwamedya_db;
CREATE USER kuwamedya_user WITH PASSWORD 'güçlü-şifre-buraya';
GRANT ALL PRIVILEGES ON DATABASE kuwamedya_db TO kuwamedya_user;
\q
```

## 📦 Adım 2: Projeyi Sunucuya Yükleme

### 1. Proje Klasörü Oluştur

```bash
sudo mkdir -p /var/www/kuwamedya
sudo chown $USER:$USER /var/www/kuwamedya
cd /var/www/kuwamedya
```

### 2. Git ile Projeyi Çek

```bash
git clone https://github.com/kullanici/kuwamedya.git .
```

**VEYA** Manuel olarak dosyaları yükleyin:

```bash
# SCP ile dosyaları yükle (kendi bilgisayarınızdan)
scp -r * kullanici@sunucu-ip:/var/www/kuwamedya/
```

### 3. Sanal Ortam Oluştur ve Aktifleştir

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Yükle

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## ⚙️ Adım 3: Yapılandırma

### 1. .env Dosyası Oluştur

```bash
cp .env.example .env
nano .env
```

**.env dosyası içeriği (Production için):**

```env
FLASK_ENV=prod
SECRET_KEY=buraya-çok-güçlü-rastgele-anahtar
DATABASE_URL=postgresql://kuwamedya_user:güçlü-şifre-buraya@localhost/kuwamedya_db
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

**SECRET_KEY oluşturma:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Veritabanı Migration'ları

```bash
# Aktif sanal ortamda
flask db upgrade

# İsterseniz örnek verileri yükleyin (dikkatli!)
flask seed
```

**NOT:** Production'da seed komutunu kullanmadan önce admin şifresini değiştirmeyi unutmayın!

## 🚀 Adım 4: Gunicorn ile Çalıştırma

### 1. Gunicorn Config Dosyası Oluştur

```bash
nano /var/www/kuwamedya/gunicorn_config.py
```

**gunicorn_config.py içeriği:**

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### 2. Systemd Service Dosyası Oluştur

```bash
sudo nano /etc/systemd/system/kuwamedya.service
```

**kuwamedya.service içeriği:**

```ini
[Unit]
Description=KUWAMEDYA Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kuwamedya
Environment="PATH=/var/www/kuwamedya/venv/bin"
ExecStart=/var/www/kuwamedya/venv/bin/gunicorn \
    --config gunicorn_config.py \
    "app:create_app()"

[Install]
WantedBy=multi-user.target
```

**NOT:** `User=www-data` kısmını kendi kullanıcı adınızla değiştirin.

### 3. Servisi Başlat

```bash
sudo systemctl daemon-reload
sudo systemctl start kuwamedya
sudo systemctl enable kuwamedya
sudo systemctl status kuwamedya
```

## 🌐 Adım 5: Nginx Yapılandırması

### 1. Nginx Config Dosyası

```bash
sudo nano /etc/nginx/sites-available/kuwamedya
```

**kuwamedya içeriği:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # SSL sertifikası için Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Gunicorn'a proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Statik dosyalar
    location /static {
        alias /var/www/kuwamedya/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Upload edilmiş dosyalar
    location /static/uploads {
        alias /var/www/kuwamedya/static/uploads;
    }
}
```

### 2. Siteyi Aktifleştir

```bash
sudo ln -s /etc/nginx/sites-available/kuwamedya /etc/nginx/sites-enabled/
sudo nginx -t  # Yapılandırmayı test et
sudo systemctl reload nginx
```

## 🔒 Adım 6: SSL Sertifikası (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx

# Sertifika al
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Otomatik yenileme testi
sudo certbot renew --dry-run
```

## 📁 Dosya İzinleri

```bash
# Statik dosyalar için
sudo chown -R www-data:www-data /var/www/kuwamedya/static
sudo chmod -R 755 /var/www/kuwamedya/static

# Upload klasörü için yazma izni
sudo chmod -R 775 /var/www/kuwamedya/static/uploads
```

## 🔄 Güncelleme Süreci

Projeyi güncellediğinizde:

```bash
cd /var/www/kuwamedya
source venv/bin/activate
git pull origin main  # veya master
pip install -r requirements.txt  # Yeni bağımlılıklar varsa
flask db upgrade  # Yeni migration'lar varsa
sudo systemctl restart kuwamedya
```

## 🐛 Sorun Giderme

### Logları Kontrol Et

```bash
# Gunicorn logları
sudo journalctl -u kuwamedya -f

# Nginx logları
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Uygulama logları
tail -f /var/www/kuwamedya/logs/kuwamedya.log
```

### Servisleri Yeniden Başlat

```bash
sudo systemctl restart kuwamedya
sudo systemctl restart nginx
```

### Veritabanı Bağlantı Sorunu

```bash
# PostgreSQL bağlantısını test et
psql -U kuwamedya_user -d kuwamedya_db -h localhost
```

## ✅ Deployment Kontrol Listesi

- [ ] Sunucu güncellemeleri yapıldı
- [ ] Python ve PostgreSQL kuruldu
- [ ] Proje dosyaları yüklendi
- [ ] Sanal ortam oluşturuldu ve bağımlılıklar yüklendi
- [ ] .env dosyası oluşturuldu ve SECRET_KEY değiştirildi
- [ ] Veritabanı oluşturuldu ve migration'lar uygulandı
- [ ] Gunicorn servisi kuruldu ve çalışıyor
- [ ] Nginx yapılandırıldı ve çalışıyor
- [ ] SSL sertifikası kuruldu
- [ ] Dosya izinleri ayarlandı
- [ ] Admin şifresi değiştirildi
- [ ] Firewall ayarları yapıldı (gerekirse)

## 🔐 Güvenlik Önerileri

1. **Firewall Ayarları:**
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

2. **SSH Güvenliği:**
   - SSH anahtar tabanlı giriş kullanın
   - Root login'i devre dışı bırakın
   - SSH portunu değiştirin (opsiyonel)

3. **Veritabanı Güvenliği:**
   - Güçlü şifreler kullanın
   - Sadece localhost'tan erişime izin verin

4. **Düzenli Yedekleme:**
   ```bash
   # Veritabanı yedekleme
   pg_dump -U kuwamedya_user kuwamedya_db > backup_$(date +%Y%m%d).sql
   ```

---

**Not:** Bu kılavuz genel bir rehberdir. Sunucu yapılandırmanıza göre bazı adımlar değişebilir.

