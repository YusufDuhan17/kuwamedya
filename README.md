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

## 🛠️ Kurulum (Adım Adım Detaylı Rehber)

Bu rehber, hiçbir teknik bilgisi olmayan kullanıcılar için hazırlanmıştır. Her adımı sırayla takip edin.

---

### 📥 ÖN HAZIRLIK: Gerekli Programları Yükleyin

#### 1. Python'u Yükleyin

**Python Nedir?**
- Bu proje Python programlama dili ile yazılmıştır.
- Python'u yüklemeden projeyi çalıştıramazsınız.

**Nasıl Yüklenir?**
1. Tarayıcınızda şu adrese gidin: https://www.python.org/downloads/
2. "Download Python" butonuna tıklayın (en son sürümü indirin, örn: Python 3.11 veya 3.12)
3. İndirilen dosyayı çalıştırın (örn: `python-3.12.0-amd64.exe`)
4. **ÖNEMLİ:** Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin! ✅
5. "Install Now" butonuna tıklayın ve kurulumun bitmesini bekleyin.
6. Kurulum bittikten sonra bilgisayarınızı yeniden başlatın.

**Kontrol Edin:**
- Windows'ta: `Win + R` tuşlarına basın, `cmd` yazın ve Enter'a basın.
- Açılan siyah pencerede (Terminal/Powershell) şu komutu yazın:
  ```bash
  python --version
  ```
- Ekranda `Python 3.12.0` gibi bir sürüm numarası görünüyorsa başarılı! ✅

---

### 🔽 ADIM 1: Projeyi İndirin ve Terminal'i Açın

1. GitHub sayfasına gidin: **https://github.com/YusufDuhan17/kuwamedya**
2. Sayfanın sağ üst kısmındaki yeşil **"Code"** butonuna tıklayın
3. Açılan menüden **"Download ZIP"** seçeneğine tıklayın
4. İndirilen ZIP dosyasını bulun (genellikle İndirilenler klasöründe)
5. ZIP dosyasına sağ tıklayın ve **"Extract All"** (Tümünü Çıkar) seçin
6. Çıkarma işlemi tamamlandıktan sonra `kuwamedya` klasörüne gidin
7. **Terminal'i Açın:**
   - `kuwamedya` klasörünün içinde boş bir yerde `Shift + Sağ Tık` yapın
   - Açılan menüden **"PowerShell penceresini burada aç"** veya **"Terminal'i burada aç"** seçeneğine tıklayın
   - Siyah bir pencere (Terminal/PowerShell) açılacak

**📌 Terminal'de Proje Klasöründe Olduğunuzu Kontrol Edin:**
- Terminal penceresinde komut satırının sonunda `kuwamedya` yazısını görmelisiniz
- Örnek: `C:\Users\Kullanici\Desktop\kuwamedya>` veya `PS C:\Users\Kullanici\Desktop\kuwamedya>`
- Eğer `kuwamedya` yazısını görmüyorsanız:
  1. Terminal penceresinde şu komutu yazın ve Enter'a basın:
     ```bash
     cd kuwamedya
     ```
  2. Veya tam yolunu kullanın (Masaüstüne çıkardıysanız):
     ```bash
     cd C:\Users\KULLANICI_ADINIZ\Desktop\kuwamedya
     ```
     (Not: `KULLANICI_ADINIZ` kısmını kendi Windows kullanıcı adınızla değiştirin)
  3. Tekrar kontrol edin: Komut satırının sonunda `kuwamedya` görünüyor mu?

---

### 🐍 ADIM 2: Sanal Ortam Oluşturun

**Sanal Ortam Nedir?**
- Projenin kendi Python paketlerini tutmak için izole bir alan oluşturur.
- Bilgisayarınızdaki diğer Python projeleriyle karışmaz.

**Windows'ta Nasıl Yapılır?**

1. **Terminal'de proje klasöründe olduğunuzdan emin olun:**
   - Komut satırının sonunda `kuwamedya` yazısı görünüyor olmalı
   - Örnek: `C:\Users\Kullanici\Desktop\kuwamedya>` veya `PS C:\Users\Kullanici\Desktop\kuwamedya>`
   - Eğer görünmüyorsa, yukarıdaki "Terminal'de Proje Klasöründe Olduğunuzu Kontrol Edin" bölümündeki adımları takip edin
2. Şu komutu yazın ve Enter'a basın:
   ```bash
   python -m venv venv
   ```
   - Bu komut `venv` adında bir klasör oluşturur (birkaç saniye sürebilir)
   - Hata mesajı görmezseniz başarılı! ✅

3. Sanal ortamı aktifleştirin:
   ```bash
   venv\Scripts\activate
   ```
   - Komut satırının başında `(venv)` yazısı görünüyorsa başarılı! ✅
   - Örnek: `(venv) C:\Users\Kullanici\Desktop\kuwamedya>`

**Linux/Mac'te:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 📦 ADIM 3: Gerekli Paketleri (Bağımlılıkları) Yükleyin

**Bağımlılık Nedir?**
- Projenin çalışması için gerekli Python kütüphaneleridir (Flask, SQLAlchemy vb.)

**Nasıl Yüklenir?**

1. **Terminal'de proje klasöründe olduğunuzdan emin olun:**
   - Komut satırının sonunda `kuwamedya` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `cd kuwamedya` komutunu çalıştırın

2. **Sanal ortamın aktif olduğundan emin olun:**
   - Komut satırının başında `(venv)` yazısı görünüyor olmalı
   - Örnek: `(venv) C:\Users\Kullanici\Desktop\kuwamedya>`
   - Eğer `(venv)` görünmüyorsa, şu komutu çalıştırın:
     ```bash
     venv\Scripts\activate
     ```
3. Şu komutu yazın ve Enter'a basın:
   ```bash
   pip install -r requirements.txt
   ```
   - Bu işlem 2-5 dakika sürebilir (internet hızınıza bağlı)
   - Ekranda birçok paket yüklendiğini göreceksiniz
   - En sonda "Successfully installed..." mesajı görünüyorsa başarılı! ✅
   - Hata alırsanız, önce şu komutu çalıştırın: `pip install --upgrade pip`

**Not:** İlk defa yapıyorsanız bu adım biraz uzun sürebilir, sabırlı olun.

---

### ⚙️ ADIM 4: Ortam Değişkenlerini Ayarlayın

**.env Dosyası Nedir?**
- Projenin gizli ayarlarını (şifreler, veritabanı bağlantısı vb.) tutar.
- Bu dosya GitHub'a yüklenmez (güvenlik için).

**Nasıl Yapılır?**

1. Proje klasöründe `.env.example` adında bir dosya göreceksiniz
2. Bu dosyayı kopyalayın ve adını `.env` yapın:
   - **Windows'ta:**
     - Dosyayı sağ tıklayın → "Kopyala"
     - Aynı klasörde boş bir yerde sağ tıklayın → "Yapıştır"
     - Yeni dosyanın adını `.env` olarak değiştirin (`.env.example` değil!)
   - **Terminal ile (Kolay Yol):**
     ```bash
     copy .env.example .env
     ```
     veya (PowerShell'de):
     ```bash
     Copy-Item .env.example .env
     ```

3. `.env` dosyasını bir metin editörü ile açın (Notepad, VS Code, Notepad++ vb.)
4. Dosyanın içeriği şöyle olmalı:
   ```env
   FLASK_ENV=dev
   SECRET_KEY=your-secret-key-here
   DEV_DATABASE_URL=sqlite:///instance/kuwamedyadb-dev.db
   ```

5. **SECRET_KEY'i Değiştirin (Çok Önemli!):**
   - Terminal'de şu komutu çalıştırın:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Ekranda uzun bir harf ve rakam dizisi görünecek (örn: `a1b2c3d4e5f6...`)
   - Bu diziyi kopyalayın
   - `.env` dosyasında `SECRET_KEY=your-secret-key-here` satırını bulun
   - `your-secret-key-here` kısmını silin ve kopyaladığınız gizli anahtarı yapıştırın
   - Örnek: `SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`

6. Dosyayı kaydedin ve kapatın.

**ÖNEMLİ:** `.env` dosyasını asla başkalarıyla paylaşmayın! GitHub'a yüklemeyin!

---

### 💾 ADIM 5: Veritabanını Oluşturun

**Veritabanı Nedir?**
- Projenin tüm bilgilerini (kullanıcılar, kurslar, projeler vb.) saklar.

**Nasıl Oluşturulur?**

1. **Terminal'de proje klasöründe olduğunuzdan emin olun:**
   - Komut satırının sonunda `kuwamedya` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `cd kuwamedya` komutunu çalıştırın

2. **Sanal ortamın aktif olduğundan emin olun:**
   - Komut satırının başında `(venv)` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `venv\Scripts\activate` komutunu çalıştırın
3. Şu komutu yazın ve Enter'a basın:
   ```bash
   flask db upgrade
   ```
   - Bu komut veritabanı tablolarını oluşturur
   - "Running upgrade" mesajları görünüyorsa başarılı! ✅
   - Hata alırsanız, önce şu komutları sırayla çalıştırın:
     ```bash
     flask db init
     flask db migrate -m "Initial migration"
     flask db upgrade
     ```

3. `instance` klasöründe `kuwamedyadb-dev.db` adında bir dosya oluşmuş olmalı (bu veritabanınızdır)

---

### 🌱 ADIM 6: Veritabanını Örnek Verilerle Doldurun

**Seed Nedir?**
- Veritabanını örnek verilerle doldurmak için kullanılır (test için).

**Nasıl Yapılır?**

1. **Terminal'de proje klasöründe olduğunuzdan emin olun:**
   - Komut satırının sonunda `kuwamedya` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `cd kuwamedya` komutunu çalıştırın

2. **Sanal ortamın aktif olduğundan emin olun:**
   - Komut satırının başında `(venv)` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `venv\Scripts\activate` komutunu çalıştırın

3. Terminal'de şu komutu yazın ve Enter'a basın:
   ```bash
   flask seed
   ```
   - Bu işlem 30-60 saniye sürebilir
   - Ekranda birçok "başarıyla eklendi" mesajı göreceksiniz
   - En sonda "Veritabanı başarıyla tohumlandı" mesajı görünüyorsa başarılı! ✅

**Bu komut ne yapar?**
- ✅ Admin kullanıcısı oluşturur
- ✅ Örnek kurslar, dersler ve quizler ekler
- ✅ Örnek projeler ve personel ekler
- ✅ Örnek hizmet paketleri ekler

**Varsayılan Admin Giriş Bilgileri:**
- **Kullanıcı Adı:** `admin`
- **E-posta:** `admin@kuwamedya.com`
- **Şifre:** `Kuwamedya2025!Admin`
- ⚠️ **ÖNEMLİ:** İlk girişten sonra mutlaka şifrenizi değiştirin! (Sidebar'dan "Şifre Değiştir" menüsünü kullanabilirsiniz)

---

### 🚀 ADIM 7: Uygulamayı Başlatın

**Uygulamayı Çalıştırma:**

1. **Terminal'de proje klasöründe olduğunuzdan emin olun:**
   - Komut satırının sonunda `kuwamedya` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `cd kuwamedya` komutunu çalıştırın

2. **Sanal ortamın aktif olduğundan emin olun:**
   - Komut satırının başında `(venv)` yazısı görünüyor olmalı
   - Eğer görünmüyorsa: `venv\Scripts\activate` komutunu çalıştırın

3. Terminal'de şu komutu yazın ve Enter'a basın:
   ```bash
   flask run
   ```
   - Ekranda şu mesajları göreceksiniz:
     ```
     * Running on http://127.0.0.1:5000
     Press CTRL+C to quit
     ```
   - Bu, uygulamanın başarıyla çalıştığı anlamına gelir! ✅

5. Tarayıcınızı açın ve şu adrese gidin:
   ```
   http://127.0.0.1:5000
   ```
   veya
   ```
   http://localhost:5000
   ```

6. Ana sayfa görünüyorsa kurulum başarılı! 🎉

**Uygulamayı Durdurma:**
- Terminal penceresinde `Ctrl + C` tuşlarına basın

---

### 🎯 HIZLI BAŞLATMA (Tekrar Çalıştırırken)

Projeyi bir sonraki sefer çalıştırmak için:

1. Proje klasörüne gidin
2. Terminal'i açın (klasör içinde `Shift + Sağ Tık` → "Terminal'i burada aç")
3. Şu komutları sırayla çalıştırın:
   ```bash
   venv\Scripts\activate
   flask run
   ```

**Not:** Windows'ta `start.bat` veya `start_dev.bat` dosyalarını çift tıklayarak da başlatabilirsiniz (otomatik olarak yukarıdaki adımları yapar).

---

### ⚠️ SIK KARŞILAŞILAN SORUNLAR VE ÇÖZÜMLERİ

#### Sorun 1: "python komutu bulunamadı" veya "'python' is not recognized"
**Çözüm:**
- Python'u PATH'e eklemediniz. Python'u yeniden yükleyin ve "Add Python to PATH" seçeneğini işaretleyin.
- Veya `python3` komutunu deneyin: `python3 -m venv venv`

#### Sorun 2: "pip komutu bulunamadı"
**Çözüm:**
- Şu komutu çalıştırın: `python -m pip install -r requirements.txt`

#### Sorun 3: "Port 5000 zaten kullanılıyor"
**Çözüm:**
- Farklı bir port kullanın: `flask run --port 5001`
- Tarayıcıda `http://127.0.0.1:5001` adresine gidin

#### Sorun 4: Veritabanı hatası
**Çözüm:**
- Veritabanını sıfırlayın:
  ```bash
  # instance klasöründeki veritabanı dosyasını silin
  del instance\kuwamedyadb-dev.db
  # Yeniden oluşturun
  flask db upgrade
  flask seed
  ```

#### Sorun 5: "ModuleNotFoundError: No module named 'xxx'"
**Çözüm:**
- Sanal ortamı aktifleştirdiğinizden emin olun (`(venv)` görünüyor olmalı)
- Bağımlılıkları yeniden yükleyin: `pip install -r requirements.txt`

---

### ✅ Kurulum Kontrol Listesi

Kurulumun başarılı olduğunu kontrol etmek için:

- [ ] Python yüklü ve `python --version` çalışıyor
- [ ] Proje klasörüne indirildi
- [ ] Sanal ortam oluşturuldu ve aktif (`(venv)` görünüyor)
- [ ] `requirements.txt` dosyasındaki paketler yüklendi
- [ ] `.env` dosyası oluşturuldu ve `SECRET_KEY` değiştirildi
- [ ] `flask db upgrade` başarıyla çalıştı
- [ ] `flask seed` başarıyla çalıştı
- [ ] `flask run` komutu çalışıyor ve tarayıcıda site açılıyor
- [ ] Admin paneline giriş yapabiliyorsunuz (admin / Kuwamedya2025!Admin)

Hepsi tamamlandıysa, kurulum başarılı! 🎉

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

## 🐛 Sorun Giderme

Daha detaylı sorun giderme bilgileri için yukarıdaki **"⚠️ SIK KARŞILAŞILAN SORUNLAR VE ÇÖZÜMLERİ"** bölümüne bakın.

## 📄 Lisans

Bu proje özel bir projedir. Tüm hakları saklıdır.

## 👤 İletişim

Sorularınız için: sahinyusufduhan@gmail.com

---

**Not:** Bu proje production için hazırlanmıştır. Deploy etmeden önce güvenlik ayarlarını kontrol ettiğinizden emin olun.

