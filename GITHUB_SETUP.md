# 📦 GitHub'a Yükleme Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. GitHub'da Repository Oluşturun

1. GitHub'a giriş yapın: https://github.com
2. Sağ üstteki "+" butonuna tıklayın → "New repository"
3. Repository adı: `kuwamedya` (veya istediğiniz isim)
4. **Private** seçin (önerilir - güvenlik için)
5. "Create repository" butonuna tıklayın

### 2. Projeyi GitHub'a Yükleyin

Proje klasörünüzde terminali açın ve şu komutları çalıştırın:

```bash
# Git repository zaten başlatıldı (git init yapıldı)

# Tüm dosyaları ekle
git add .

# İlk commit'i yap
git commit -m "Initial commit: KUWAMEDYA project"

# GitHub repository'nizi ekleyin (URL'yi kendi repository'nizle değiştirin)
git remote add origin https://github.com/KULLANICI_ADINIZ/kuwamedya.git

# Ana branch'i main olarak ayarlayın
git branch -M main

# GitHub'a yükleyin
git push -u origin main
```

**NOT:** GitHub kullanıcı adınız ve repository adınızı değiştirmeyi unutmayın!

### 3. Güvenlik Kontrolü

GitHub'a yüklemeden önce şunları kontrol edin:

✅ `.env` dosyası **YOK** (`.gitignore`'da olmalı)
✅ `ADMIN_BILGILERI.txt` **YOK** (`.gitignore`'da olmalı)
✅ `venv/` klasörü **YOK** (`.gitignore`'da olmalı)
✅ `*.db` dosyaları **YOK** (`.gitignore`'da olmalı)
✅ `logs/` klasörü **YOK** (`.gitignore`'da olmalı)
✅ `.env.example` **VAR** (örnek dosya, yüklenmeli)

Kontrol etmek için:
```bash
git status
```

## 📝 Dosya Yapısı

GitHub'a yüklenecek dosyalar:
- ✅ Tüm Python dosyaları (`.py`)
- ✅ Tüm template dosyaları (`.html`)
- ✅ CSS ve JavaScript dosyaları
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `.env.example` (örnek dosya)
- ✅ `DEPLOYMENT.md`
- ✅ `SECURITY.md`

GitHub'a yüklenmeyecek dosyalar (`.gitignore` sayesinde):
- ❌ `.env` (gizli bilgiler)
- ❌ `venv/` (sanal ortam)
- ❌ `*.db` (veritabanı dosyaları)
- ❌ `logs/` (log dosyaları)
- ❌ `ADMIN_BILGILERI.txt` (gizli bilgiler)

## 🔐 Güvenlik Notları

### Bülent Bey için Önemli:

1. **Repository'yi Private Yapın:**
   - GitHub'da repository ayarlarına gidin
   - Settings → General → Danger Zone → Change visibility → Make private

2. **.env Dosyasını ASLA Yüklemeyin:**
   - `.gitignore` dosyası bunu engelliyor ama kontrol edin
   - Eğer yanlışlıkla yüklendiyse:
     ```bash
     git rm --cached .env
     git commit -m "Remove .env from repository"
     git push
     ```
     **VE** GitHub'da Settings → Secrets → New secret ile `.env` içeriğini ekleyin

3. **SECRET_KEY'i Değiştirin:**
   - Production'da mutlaka yeni bir SECRET_KEY kullanın
   - `python -c "import secrets; print(secrets.token_hex(32))"` ile oluşturun

## 📤 Güncelleme Yapmak

Projede değişiklik yaptıktan sonra:

```bash
# Değişiklikleri göster
git status

# Tüm değişiklikleri ekle
git add .

# Commit yap
git commit -m "Açıklayıcı commit mesajı"

# GitHub'a yükle
git push
```

## 🔄 Bülent Bey'in Sunucuya Yüklemesi

Bülent Bey projeyi GitHub'dan alıp kendi sunucusuna yükleyecek:

```bash
# Sunucuda projeyi klonlayın
git clone https://github.com/KULLANICI_ADINIZ/kuwamedya.git
cd kuwamedya

# .env dosyasını oluşturun
cp .env.example .env
nano .env  # Düzenleyin

# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanını oluşturun
flask db upgrade
flask seed  # İsterseniz

# Uygulamayı başlatın
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Detaylı kurulum için `DEPLOYMENT.md` dosyasına bakın.

## ✅ Kontrol Listesi

GitHub'a yüklemeden önce:

- [ ] `.env` dosyası `.gitignore`'da
- [ ] `ADMIN_BILGILERI.txt` `.gitignore`'da
- [ ] `venv/` klasörü `.gitignore`'da
- [ ] `*.db` dosyaları `.gitignore`'da
- [ ] `logs/` klasörü `.gitignore`'da
- [ ] `.env.example` dosyası var ve dolu
- [ ] `README.md` dosyası var ve güncel
- [ ] `SECRET_KEY` production'da değiştirilecek (şimdilik OK)
- [ ] Repository Private olarak ayarlandı (önerilir)

## 🎯 Sonraki Adımlar

1. ✅ GitHub repository oluşturuldu
2. ✅ Proje GitHub'a yüklendi
3. ⏳ Bülent Bey projeyi klonlayacak
4. ⏳ Sunucuya deploy edilecek
5. ⏳ Domain bağlanacak
6. ⏳ SSL sertifikası kurulacak

---

**İyi çalışmalar! 🚀**

