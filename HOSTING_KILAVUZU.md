# 🌐 Web Sitesi Olarak Yayınlama Kılavuzu

Projenizi canlı bir web sitesine dönüştürmek için birkaç seçenek var. En kolay ve hızlı yöntemler:

## 🚀 Seçenek 1: Render.com (ÖNERİLEN - En Kolay)

**Avantajlar:**
- ✅ Ücretsiz tier var
- ✅ Kolay kurulum (GitHub bağlantısı)
- ✅ Otomatik SSL sertifikası (HTTPS)
- ✅ Özel domain ekleme
- ✅ PostgreSQL veritabanı desteği

### Adımlar:

1. **Render.com'a kaydolun:**
   - https://render.com → Sign Up
   - GitHub hesabınızla giriş yapın

2. **Yeni Web Service Oluşturun:**
   - Dashboard → "New +" → "Web Service"
   - GitHub repository'nizi seçin: `YusufDuhan17/kuwamedya`
   - Branch: `main`

3. **Ayarları Yapın:**
   ```
   Name: kuwamedya (veya istediğiniz isim)
   Region: Frankfurt (veya en yakın)
   Branch: main
   Root Directory: (boş bırakın)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"
   ```

4. **Environment Variables (Ortam Değişkenleri) Ekleyin:**
   ```
   FLASK_ENV=prod
   SECRET_KEY=buraya-güçlü-rastgele-anahtar-yazın
   DATABASE_URL=postgresql://... (Render otomatik oluşturur)
   ```
   
   **SECRET_KEY oluşturma:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **PostgreSQL Database Oluşturun:**
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `kuwamedya-db`
   - Plan: Free
   - "Create Database" tıklayın
   - Database URL'ini kopyalayın
   - Web Service ayarlarına geri dönün
   - Environment Variables'a ekleyin: `DATABASE_URL=postgresql://...`

6. **Deploy Edin:**
   - "Create Web Service" tıklayın
   - İlk deploy 5-10 dakika sürebilir

7. **Domain Ekleme (İsteğe Bağlı):**
   - Settings → Custom Domains
   - Domain adınızı ekleyin (örn: `www.kuwamedya.com`)
   - DNS ayarlarını yapın (Render size talimat verir)

**URL Formatı:** `https://kuwamedya.onrender.com` (veya verdiğiniz isim)

---

## 🚀 Seçenek 2: Railway.app (Kolay)

**Avantajlar:**
- ✅ Ücretsiz tier (aylık $5 kredi)
- ✅ GitHub entegrasyonu
- ✅ Otomatik SSL

### Adımlar:

1. **Railway'a kaydolun:**
   - https://railway.app → Sign Up with GitHub

2. **Yeni Proje:**
   - "New Project" → "Deploy from GitHub repo"
   - `YusufDuhan17/kuwamedya` seçin

3. **Ayarlar:**
   - Railway otomatik algılar
   - Environment Variables ekleyin:
     ```
     FLASK_ENV=prod
     SECRET_KEY=güçlü-anahtar
     ```

4. **PostgreSQL Ekle:**
   - "+ New" → "Database" → "Add PostgreSQL"
   - Railway otomatik `DATABASE_URL` ekler

5. **Domain:**
   - Settings → Generate Domain (veya Custom Domain ekleyin)

---

## 🚀 Seçenek 3: DigitalOcean App Platform

**Avantajlar:**
- ✅ Kolay kurulum
- ✅ İyi performans
- ✅ Ücretsiz tier var (sınırlı)

### Adımlar:

1. https://www.digitalocean.com → Sign Up
2. "Create" → "Apps" → "GitHub" seçin
3. Repository'nizi seçin
4. Ayarları yapın (Railway'a benzer)
5. Deploy edin

---

## 🚀 Seçenek 4: VPS (Kendi Sunucunuz)

**Avantajlar:**
- ✅ Tam kontrol
- ✅ Daha fazla özelleştirme
- ✅ Daha ucuz (uzun vadede)

**Dezavantajlar:**
- ❌ Teknik bilgi gerekir
- ❌ Sunucu yönetimi sizde

Detaylı talimatlar için `DEPLOYMENT.md` dosyasına bakın.

---

## 📋 Hangi Seçeneği Seçmeliyim?

### İlk Kez Yapıyorsanız:
→ **Render.com** (En kolay, ücretsiz)

### Daha Fazla Kontrol İsterseniz:
→ **Railway.app** (Kolay, esnek)

### Profesyonel ve Büyük Ölçekli:
→ **VPS + DigitalOcean/Droplet** (Teknik, güçlü)

---

## 🔧 Deployment Öncesi Kontrol Listesi

- [ ] `.env` dosyası GitHub'a yüklenmedi (güvenlik)
- [ ] `SECRET_KEY` güçlü ve benzersiz
- [ ] `FLASK_ENV=prod` ayarlandı
- [ ] PostgreSQL veritabanı hazır
- [ ] Domain hazırsa DNS ayarları yapıldı

---

## 🌍 Domain Bağlama

### Render.com'da:

1. Settings → Custom Domains
2. Domain adınızı ekleyin (örn: `www.kuwamedya.com`)
3. Render size DNS kayıtlarını verir:
   ```
   Type: CNAME
   Name: www
   Value: kuwamedya.onrender.com
   ```
4. Domain sağlayıcınızda (GoDaddy, Namecheap vb.) bu DNS kayıtlarını ekleyin
5. 24-48 saat içinde aktif olur

### SSL Sertifikası:
- Render otomatik Let's Encrypt SSL ekler (HTTPS)
- Ücretsiz ve otomatik yenilenir

---

## 📞 Destek

Sorun yaşarsanız:
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- DigitalOcean: https://docs.digitalocean.com

---

**Önerilen:** Render.com ile başlayın - en kolay ve hızlı! 🚀

