import os
from dotenv import load_dotenv
from datetime import timedelta

# ==========================================================================
# Geliştirilmiş Konfigürasyon Dosyası (config.py)
# Sürüm: v5.0 (Kusursuz & Ultra Donanımlı)
#
# YENİLİKLER VE "KUSURSUZ" GÜNCELLEMELER:
# 1.  HATA GİDERİLDİ (ValueError):
#     'ProductionConfig' sınıfı, 'flask run' komutu sırasında, daha
#     kullanılmadan 'import' edildiği anda çöküyordu. 'DATABASE_URL'
#     kontrolü kaldırıldı. Bu kontrol sunucu (örn: Heroku, Render)
#     seviyesinde yapılmalıdır, kod seviyesinde değil.
#
# 2.  FLASK_ENV GARANTİSİ:
#     'FLASK_ENV' ortam değişkeni, temel 'Config' sınıfına eklendi.
#     Bu, 'app.py'nin 'FLASK_ENV' ayarlanmamış olsa bile
#     HER ZAMAN 'dev' (Development) modunu varsayılan olarak
#     seçmesini garantiler.
#
# 3.  GÜVENLİK İYİLEŞTİRMELERİ: 'SESSION_COOKIE_SECURE' ve
#     'SESSION_COOKIE_HTTPONLY' ayarları canlı (production) ortam için
#     varsayılan olarak True yapıldı. Bu, oturum güvenliğini artırır.
#
# 4.  MERKEZİLEŞTİRME: 'COMMISSION_RATE' (prim oranı) ve
#     'GOOGLE_CLIENT_ID' gibi kritik ayarlar merkezi olarak burada
#     toplandı ve '.env' dosyasından okunuyor.
# ==========================================================================

# Projenin kök dizinini bul ve .env dosyasını yükle
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Tüm ortamlar için ortak olan temel yapılandırma sınıfı."""
    
    # --- TEMEL UYGULAMA AYARLARI ---
    # GÜNCELLEME: FLASK_ENV ayarını burada garantiliyoruz.
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'dev'
    # GÜVENLİK: Production'da mutlaka SECRET_KEY ortam değişkeni ayarlanmalı!
    # Development için fallback değer, production'da kullanılmamalı
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DEV-ONLY-FALLBACK-KEY-CHANGE-IN-PRODUCTION'
    DEBUG = False
    TESTING = False
    
    # --- VERİTABANI AYARLARI ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Varsayılan olarak SQLite kullanılır, ortam değişkeniyle ezilebilir.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'kuwamedyadb.db')

    # --- OTURUM (SESSION) AYARLARI ---
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # --- DOSYA YÜKLEME AYARLARI ---
    # GÜNCELLEME: Yükleme klasörünü 'static/uploads' olarak ayarlıyoruz
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maksimum yükleme boyutu: 16 MB

    # --- KUWAMEDYA ÖZEL AYARLARI ---
    COMMISSION_RATE = 0.10 # Prim hesaplama oranı (%10)

    # --- GOOGLE OAUTH AYARLARI ---
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_REDIRECT_URI = '/auth/google/callback'


class DevelopmentConfig(Config):
    """Geliştirme ortamı (senin bilgisayarın) için özel ayarlar."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'kuwamedyadb-dev.db')
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Canlı sunucu (production) ortamı için özel ayarlar."""
    DEBUG = False
    
    # Canlı ortamda veritabanı URL'si ortam değişkeninden gelmeli
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # GÜNCELLEME: HATA GİDERİLDİ!
    # 'raise ValueError' satırı kaldırıldı. Bu kontrol, sunucu
    # seviyesinde yapılmalıdır, kod import edilirken değil.
    # if not SQLALCHEMY_DATABASE_URI:
    #     raise ValueError("Canlı ortam için DATABASE_URL ortam değişkeni ayarlanmamış!")
        
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


# Farklı ortamlar için konfigürasyonları bir sözlükte topluyoruz.
config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig,
    default=DevelopmentConfig # Varsayılan ortam: geliştirme
)

key = Config.SECRET_KEY
