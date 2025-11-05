# 🔒 Güvenlik Politikası ve Önerileri

## Güvenlik Açıkları Bildirimi

Eğer bir güvenlik açığı keşfettiyseniz, lütfen doğrudan GitHub Issues'da paylaşmayın. Bunun yerine proje sahibiyle özel olarak iletişime geçin.

## Güvenlik Önlemleri

### 1. Ortam Değişkenleri

**ASLA** aşağıdaki bilgileri kod içinde hardcode etmeyin:
- `SECRET_KEY`
- Veritabanı şifreleri
- API anahtarları
- OAuth client secret'ları

Bu bilgileri `.env` dosyasında saklayın ve `.env` dosyasını `.gitignore`'a ekleyin.

### 2. Production Ortamı

Production ortamında mutlaka:
- ✅ HTTPS kullanın
- ✅ Güçlü `SECRET_KEY` kullanın (en az 32 karakter rastgele string)
- ✅ `DEBUG = False` ayarında çalıştırın
- ✅ Veritabanı şifrelerini güvenli tutun
- ✅ Düzenli yedekleme yapın

### 3. Veritabanı Güvenliği

- Production'da mutlaka PostgreSQL veya MySQL kullanın
- SQLite sadece development için uygundur
- Veritabanı kullanıcısı için güçlü şifreler kullanın
- Mümkünse sadece localhost'tan erişime izin verin

### 4. Şifre Politikası

- Admin şifreleri en az 12 karakter olmalı
- Büyük/küçük harf, sayı ve özel karakter içermeli
- Düzenli olarak değiştirilmeli

### 5. Session Güvenliği

- `SESSION_COOKIE_SECURE = True` (HTTPS için)
- `SESSION_COOKIE_HTTPONLY = True` (XSS koruması)
- `SESSION_COOKIE_SAMESITE = 'Lax'` (CSRF koruması)

### 6. Dosya Yükleme Güvenliği

- Sadece izin verilen dosya tipleri yüklenebilir
- Dosya boyutu limiti var (16 MB)
- Yüklenen dosyalar `static/uploads/` klasöründe saklanır

### 7. CSRF Koruması

Flask-WTF ile otomatik CSRF koruması aktif. Tüm formlar CSRF token içermelidir.

### 8. SQL Injection Koruması

SQLAlchemy ORM kullanıldığı için SQL injection riski minimize edilmiştir. Ancak raw SQL sorguları kullanırken dikkatli olun.

### 9. XSS Koruması

Jinja2 template engine otomatik olarak HTML escape yapar. Ancak `|safe` filtresi kullanırken dikkatli olun.

## Güvenlik Kontrol Listesi

Deployment öncesi kontrol edin:

- [ ] `.env` dosyası `.gitignore`'da
- [ ] `SECRET_KEY` güçlü ve benzersiz
- [ ] `DEBUG = False` (production'da)
- [ ] HTTPS aktif
- [ ] Veritabanı şifreleri güçlü
- [ ] Admin şifreleri değiştirildi
- [ ] Firewall ayarları yapıldı
- [ ] Düzenli yedekleme planı var
- [ ] Log dosyaları güvenli saklanıyor
- [ ] SSL sertifikası geçerli

## Güncelleme ve Yama

Düzenli olarak:
- Python paketlerini güncelleyin: `pip install --upgrade -r requirements.txt`
- Güvenlik yamalarını takip edin
- Bağımlılıkları kontrol edin: `pip list --outdated`

## Loglama ve İzleme

- Hata logları düzenli kontrol edilmeli
- Şüpheli aktiviteler izlenmeli
- Başarısız giriş denemeleri loglanıyor

---

**Son Güncelleme:** 2025

