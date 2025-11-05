from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

# ==========================================================================
# Geliştirilmiş Eklenti Başlatma (extensions.py) - v2.1 (OAuth Kaldırıldı)
#
# YENİLİKLER (v2.1):
# - Google OAuth eklentisi kaldırıldı.
# ==========================================================================

# --- VERİTABANI EKLENTİSİ ---
# SQLAlchemy: Python sınıfları (modeller) ile veritabanı işlemleri için ORM.
db = SQLAlchemy()

# --- ŞİFRELEME EKLENTİSİ ---
# Bcrypt: Kullanıcı şifrelerini güvenli hash'lemek için.
bcrypt = Bcrypt()

# --- KULLANICI OTURUM YÖNETİMİ EKLENTİSİ ---
# LoginManager: Kullanıcı giriş/çıkış, oturum yönetimi ("Beni Hatırla" vb.).
login_manager = LoginManager()

# --- VERİTABANI GÖÇ YÖNETİMİ EKLENTİSİ ---
# Migrate: SQLAlchemy modellerindeki değişiklikleri veritabanına uygulamak için (Alembic kullanır).
migrate = Migrate()