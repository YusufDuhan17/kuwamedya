import os
import secrets
from PIL import Image
from flask import current_app
from extensions import db
from models import ActivityLog

# ===================================================================
# KUWAMEDYA - YARDIMCI FONKSİYONLAR (utils.py)
# Sürüm: v5.0 (Kusursuz & Ultra Donanımlı)
#
# BU DOSYA, PROJENİN TAMAMINDA TEKRAR EDEN İŞLEVLERİ (örn: resim
# kaydetme, aktivite loglama) TEK BİR MERKEZDE TOPLAR.
#
# "TOP SEVİYE" GÜNCELLEMELERİ:
# 1.  MERKEZİLEŞTİRME (DRY PRENSİBİ):
#     Bu fonksiyonlar ('save_picture', 'log_activity') daha önce
#     'admin_routes.py' ve 'academy_routes.py' içinde tekrar ediyordu.
#     Tüm kod tekrarı giderildi. Artık tüm 'routes' dosyaları
#     bu merkezi fonksiyonları 'from utils import ...' ile çağıracak.
#
# 2.  GÜÇLENDİRİLMİŞ 'save_picture':
#     - 'UPLOAD_FOLDER' ve 'ALLOWED_EXTENSIONS' gibi ayarları
#       doğrudan 'current_app.config' üzerinden okur.
#     - 'folder' parametresi ile ('profile_pics', 'courses' vb.)
#       alt klasörlere dinamik olarak kayıt yapabilir.
#     - Resimleri kaydederken 'quality=85, optimize=True'
#       parametreleri ile web için optimize eder.
#
# 3.  GÜVENLİ 'log_activity':
#     Loglama işlemi sırasında bir hata oluşursa (örn: 'target'
#     nesnesi hatalıysa), 'try...except' bloğu sayesinde
#     ana işlemi (örn: satış ekleme) durdurmaz, sadece hatayı loglar.
# ===================================================================

def save_picture(form_picture, folder='profile_pics', output_size=(300, 300)):
    """
    Yüklenen bir resmi yeniden boyutlandırır, optimize eder, kaydeder
    ve dosya adını (yoluyla birlikte) döndürür.
    
    Kullanım:
    save_picture(form.picture.data, folder='profile_pics', output_size=(300, 300))
    save_picture(form.cover_image.data, folder='courses', output_size=(800, 450))
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    
    # Güvenlik: İzin verilen dosya uzantılarını config'den kontrol et
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    if f_ext.lower().strip('.') not in allowed_extensions:
        raise ValueError("İzin verilmeyen dosya türü. Sadece JPG, PNG, JPEG kabul edilir.")

    picture_fn = random_hex + f_ext
    # Yükleme klasörünü config'den al (örn: /static/uploads)
    upload_folder_base = current_app.config['UPLOAD_FOLDER']
    # Alt klasörü (örn: /static/uploads/profile_pics) oluştur
    upload_subfolder = os.path.join(upload_folder_base, folder)
    picture_path = os.path.join(upload_subfolder, picture_fn)

    # Klasör yoksa oluştur (güvenli)
    os.makedirs(upload_subfolder, exist_ok=True)

    try:
        i = Image.open(form_picture)
        # Şeffaflık (RGBA) veya palet (P) modundaki resimleri RGB'ye dönüştür
        if i.mode in ("RGBA", "P"):
            i = i.convert("RGB")
        
        i.thumbnail(output_size)
        i.save(picture_path, quality=85, optimize=True) # Web için optimize et
        
        # Geriye sadece 'profile_pics/dosyaadi.jpg' gibi bir yol döndür
        # 'models.py' bu dosya adını saklayacak.
        # 'layout.html' ise 'url_for('static', filename='uploads/' + user.image_file)'
        # şeklinde tam yolu oluşturacak.
        return os.path.join(folder, picture_fn).replace("\\", "/")
    
    except Exception as e:
        current_app.logger.error(f"Resim kaydetme hatası ({picture_path}): {e}")
        raise

def log_activity(user, action, target=None):
    """
    Sistemdeki önemli olayları (örn: 'admin giriş yaptı')
    veritabanındaki ActivityLog tablosuna kaydeder.
    """
    try:
        activity = ActivityLog(user_id=user.id, action=action)
        # Eğer log bir nesneyle ilişkiliyse (örn: bir Kurs veya Proje)
        # o nesnenin tipini ve ID'sini de kaydet.
        if target and hasattr(target, 'id') and target.id:
            activity.target_type = target.__class__.__name__
            activity.target_id = target.id
        db.session.add(activity)
        # Not: Bu fonksiyon 'commit' yapmaz!
        # Onu çağıran rota (örn: add_user) kendi 'commit'ini yapmalıdır.
    except Exception as e:
        # Loglama hatası kritik değilse sadece logla, ana işlemi durdurma
        current_app.logger.error(f"Loglama hatası: {e}")
        # db.session.rollback() # Ana işlemi etkilememeli