# 🚀 Render.com Deployment - Adım Adım

## 📋 Ön Hazırlık

1. GitHub repository'niz hazır: https://github.com/YusufDuhan17/kuwamedya
2. Render.com hesabı oluşturun: https://render.com

## 🎯 Adım 1: Render.com'a Giriş

1. https://render.com → **Sign Up**
2. **"Sign up with GitHub"** seçin
3. GitHub hesabınızla giriş yapın
4. Render, GitHub repository'lerinize erişim isteyecek → **Approve** (Onayla)

## 🎯 Adım 2: PostgreSQL Database Oluştur

1. Dashboard'da **"New +"** → **"PostgreSQL"**
2. Ayarlar:
   ```
   Name: kuwamedya-db
   Database: kuwamedya
   User: kuwamedya_user
   Region: Frankfurt (veya en yakın)
   PostgreSQL Version: 15 (veya en son)
   Plan: Free (veya istediğiniz plan)
   ```
3. **"Create Database"** tıklayın
4. Database oluşturulduktan sonra:
   - **"Connections"** sekmesine gidin
   - **"Internal Database URL"** kopyalayın (sonra kullanacağız)
   - Format: `postgresql://kuwamedya_user:şifre@dpg-xxx.region.render.com/kuwamedya`

## 🎯 Adım 3: Web Service Oluştur

1. Dashboard'da **"New +"** → **"Web Service"**
2. **"Connect account"** → GitHub repository'nizi seçin: `YusufDuhan17/kuwamedya`
3. Ayarları doldurun:

### Temel Ayarlar:
```
Name: kuwamedya
Region: Frankfurt (database ile aynı)
Branch: main
Root Directory: (boş bırakın)
```

### Build & Start:
```
Runtime: Python 3
Build Command: pip install -r requirements.txt && pip install gunicorn
Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"
```

**VEYA** (daha basit):
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"
```

### Environment Variables:
**"Environment"** sekmesine gidin ve şunları ekleyin:

```
FLASK_ENV = prod
SECRET_KEY = [aşağıdaki komutla oluşturun]
DATABASE_URL = [Adım 2'de kopyaladığınız PostgreSQL URL]
```

**SECRET_KEY oluşturma:**
Kendi bilgisayarınızda terminal açın:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Çıkan değeri `SECRET_KEY` olarak ekleyin.

**Örnek Environment Variables:**
```
FLASK_ENV=prod
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
DATABASE_URL=postgresql://kuwamedya_user:şifre@dpg-xxx.region.render.com/kuwamedya
```

### Instance Type:
```
Free: (ücretsiz) - 512 MB RAM
```

## 🎯 Adım 4: Deploy

1. **"Create Web Service"** tıklayın
2. İlk deploy 5-10 dakika sürebilir
3. Logları takip edin (deploy ilerlemesini gösterir)
4. Başarılı olursa yeşil "Live" yazısı görünür

## 🎯 Adım 5: Veritabanı Migration

1. Web Service → **"Shell"** sekmesine gidin
2. Shell açıldıktan sonra:

```bash
# Migration'ları uygula
flask db upgrade

# İsterseniz örnek verileri yükleyin (dikkatli!)
flask seed
```

## 🎯 Adım 6: Siteyi Test Edin

1. Web Service'in üstündeki URL'e tıklayın
2. Format: `https://kuwamedya.onrender.com`
3. Site açılıyor mu kontrol edin

## 🌍 Adım 7: Domain Ekleme (İsteğe Bağlı)

### Render Ücretsiz Domain:
- Render otomatik bir domain verir: `kuwamedya.onrender.com`
- Bu domain SSL (HTTPS) ile gelir

### Özel Domain Ekleme:

1. **Settings** → **"Custom Domains"** sekmesi
2. **"Add Custom Domain"** tıklayın
3. Domain adınızı girin (örn: `www.kuwamedya.com`)
4. Render size DNS kayıtlarını verir:
   ```
   Type: CNAME
   Name: www
   Value: kuwamedya.onrender.com
   ```
5. Domain sağlayıcınızda (GoDaddy, Namecheap, vb.) bu DNS kayıtlarını ekleyin
6. 24-48 saat içinde aktif olur
7. Render otomatik SSL sertifikası ekler (HTTPS)

## 🔧 Sorun Giderme

### Deploy Başarısız Olursa:

1. **Logs** sekmesine bakın
2. Hata mesajını okuyun
3. Yaygın sorunlar:
   - `ModuleNotFoundError`: `requirements.txt`'e eksik paket ekleyin
   - `Database connection error`: `DATABASE_URL` doğru mu kontrol edin
   - `SECRET_KEY` hatası: Environment variable eklediğinizden emin olun

### Veritabanı Bağlantı Sorunu:

1. PostgreSQL database'in **"Connections"** sekmesine gidin
2. **"Internal Database URL"** kullanın (External değil!)
3. Environment variable'da doğru URL olduğundan emin olun

### Site Açılmıyor:

1. **Logs** sekmesinde hata var mı kontrol edin
2. **Metrics** sekmesinde CPU/RAM kullanımına bakın
3. Free tier'da bazen uyku moduna geçer (ilk açılış yavaş olabilir)

## 📊 Monitoring

- **Metrics**: CPU, RAM, Request sayıları
- **Logs**: Uygulama logları (canlı takip)
- **Events**: Deploy geçmişi

## 🔄 Güncelleme

GitHub'a push yaptığınızda Render otomatik deploy eder:

```bash
git add .
git commit -m "Update"
git push origin main
```

Render otomatik olarak yeni deploy başlatır (1-2 dakika).

## 💰 Fiyatlandırma

- **Free Tier:**
  - 512 MB RAM
  - 0.1 CPU
  - Spin down after 15 min (uyku modu)
  - 750 saat/ay

- **Starter ($7/ay):**
  - 512 MB RAM
  - 0.5 CPU
  - Her zaman çalışır
  - Özel domain

## ✅ Kontrol Listesi

- [ ] PostgreSQL database oluşturuldu
- [ ] Web Service oluşturuldu
- [ ] Environment variables eklendi (FLASK_ENV, SECRET_KEY, DATABASE_URL)
- [ ] Build Command ayarlandı
- [ ] Start Command ayarlandı
- [ ] Deploy başarılı
- [ ] Veritabanı migration yapıldı
- [ ] Site test edildi
- [ ] Domain eklendi (isteğe bağlı)

---

**Site hazır! 🎉**

URL: `https://kuwamedya.onrender.com` (veya verdiğiniz isim)

