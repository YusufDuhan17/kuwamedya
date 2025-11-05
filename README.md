# KUWAMEDYA - Dijital Ajans Web Sitesi

Flask tabanlı dijital ajans web sitesi. Tam özellikli yönetim paneli ve akademi sistemi içerir.

## 📦 Proje

Bu proje GitHub'da barındırılmaktadır: https://github.com/YusufDuhan17/kuwamedya

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

### Hızlı Kurulum (Windows)

1. **Python'u Yükleyin:**
   - https://www.python.org/downloads/ adresinden Python 3.8+ indirin
   - Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin ✅
   - Kurulumdan sonra bilgisayarı yeniden başlatın

2. **Projeyi İndirin:**
   
   **Yöntem 1: ZIP İndirme (Önerilen - Başlangıç için)**
   - GitHub sayfasına gidin: https://github.com/YusufDuhan17/kuwamedya
   - Sağ üstteki yeşil **"Code"** butonuna tıklayın
   - Açılan menüden **"Download ZIP"** seçeneğine tıklayın
   - İndirilen ZIP dosyasını bulun (genellikle `İndirilenler` klasöründe)
   - ZIP dosyasına sağ tıklayın ve **"Tümünü Çıkar"** (Extract All) seçin
   - Çıkarma işlemi tamamlandıktan sonra `kuwamedya` klasörüne gidin
   
   **Yöntem 2: Git Clone (Geliştiriciler için)**
   - Terminal/PowerShell'i açın
   - İstediğiniz klasöre gidin (örn: `cd Desktop`)
   - Şu komutu çalıştırın:
     ```bash
     git clone https://github.com/YusufDuhan17/kuwamedya.git
     ```
   - `kuwamedya` klasörüne gidin: `cd kuwamedya`

3. **Kurulum Script'ini Çalıştırın:**
   - `setup.bat` dosyasına **çift tıklayın**
   - Script otomatik olarak:
     - ✅ Sanal ortam oluşturur
     - ✅ Tüm paketleri yükler
     - ✅ `.env` dosyası oluşturur (varsa `.env.example`'dan)
     - ✅ Veritabanını oluşturur ve örnek verilerle doldurur
     - ✅ Uygulamayı başlatır ve tarayıcıyı açar

4. **İlk Giriş:**
   - Tarayıcıda `http://127.0.0.1:5000` açılacak
   - Admin paneline giriş yapın:
     - **Kullanıcı Adı:** `admin`
     - **Şifre:** `Kuwamedya2025!Admin`
   - ⚠️ **ÖNEMLİ:** İlk girişten sonra şifrenizi değiştirin!

---

### Günlük Kullanım

- `start.bat` dosyasına **çift tıklayın** → Uygulama başlar ve tarayıcı açılır
- Geliştirme yapıyorsanız: `start_dev.bat` (debug modu aktif)

---

### Manuel Kurulum (Linux/Mac veya İleri Seviye)

<details>
<summary>Detaylı kurulum adımları için tıklayın</summary>

1. **Python ve pip yüklü olmalı:**
   ```bash
   python --version  # Python 3.8+ olmalı
   ```

2. **Projeyi klonlayın:**
   ```bash
   git clone https://github.com/YusufDuhan17/kuwamedya.git
   cd kuwamedya
   ```

3. **Sanal ortam oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya
   venv\Scripts\activate  # Windows
   ```

4. **Paketleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

5. **.env dosyası oluşturun:**
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin ve SECRET_KEY'i değiştirin
   ```

6. **Veritabanını oluşturun:**
   ```bash
   flask db upgrade
   flask seed
   ```

7. **Uygulamayı başlatın:**
   ```bash
   flask run
   ```

</details>

---

### ⚠️ Sık Karşılaşılan Sorunlar

#### Sorun 1: "python komutu bulunamadı"
**Çözüm:** Python'u yeniden yükleyin ve "Add Python to PATH" seçeneğini işaretleyin.

#### Sorun 2: Projeyi başka klasöre taşıdım, hata alıyorum
**Çözüm:** `setup.bat` dosyasını tekrar çalıştırın. Eski venv'i siler ve yenisini oluşturur.

#### Sorun 3: Port 5000 zaten kullanılıyor
**Çözüm:** Farklı bir port kullanın: `flask run --port 5001`

#### Sorun 4: Veritabanı hatası
**Çözüm:** `instance\kuwamedyadb-dev.db` dosyasını silin ve `setup.bat`'ı tekrar çalıştırın.

---


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
   - İlk girişten sonra admin şifresini mutlaka değiştirin (Sidebar'dan "Şifre Değiştir" menüsünü kullanın)
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

## 📝 Notlar

- Bu proje local development için hazırlanmıştır
- Production için sunucu kurulumu gereklidir
- Tüm güvenlik ayarları `.env` dosyasında yapılmalıdır


## 📄 Lisans

Bu proje özel bir projedir. Tüm hakları saklıdır.

## 👤 İletişim

Sorularınız için: sahinyusufduhan@gmail.com

---

**Not:** Bu proje production için hazırlanmıştır. Deploy etmeden önce güvenlik ayarlarını kontrol ettiğinizden emin olun.

