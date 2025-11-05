from functools import wraps
from flask import abort
from flask_login import login_required, current_user

# ===================================================================
# Geliştirilmiş Güvenlik Dekoratörleri (decorators.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU DOSYA, PROJENİN GÜVENLİK MİMARİSİNİ TANIMLAR.
# "AKADEMİYİ HALKA AÇMA" HEDEFİMİZ DOĞRULTUSUNDA GÜNCELLENMİŞTİR.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  YENİ DEKORATÖR: `@staff_required` EKLENDİ:
#     - Bu yeni dekoratör, bir rotayı SADECE "çalışan" olanlara
#       (rolü 'Admin' VEYA 'Personel' olanlara) açar.
#     - Bu, 'Kullanıcı' (Öğrenci) rolündeki kişilerin, onlarla
#       ilgisi olmayan "Satış Ekle", "Personel Listesi" gibi
#       şirket içi sayfalara erişmesini engellemek için KRİTİKTİR.
#
# 2.  YENİ MİMARİYE UYUM:
#     - `@admin_required` dekoratörü, 'Admin'e özel sayfalar
#       (örn: Kurs Yönetimi) için korunmuştur.
#     - `@staff_required` dekoratörü, personele özel sayfalar
#       (örn: Satış Listesi) için kullanılacaktır.
#     - `flask_login`'in kendi `@login_required` dekoratörü ise
#       artık Akademi gibi TÜM giriş yapmış kullanıcıların
#       (Admin, Personel VE Kullanıcı) görebileceği sayfaları
#       korumak için kullanılacaktır.
#
# 3.  MODEL ENTEGRASYONU:
#     - Yeni dekoratörler, `models.py` dosyasına eklediğimiz
#       `current_user.is_admin` ve `current_user.is_staff`
#       yardımcı metotlarını (property) kullanır.
# ===================================================================

def admin_required(f):
    """
    Bir rotanın SADECE 'Admin' rolüne sahip kullanıcılar tarafından
    erişilebilir olmasını sağlayan dekoratör. (v5.0)
    
    Kullanım:
    @admin.route('/manage_courses')
    @login_required
    @admin_required  <-- BU FONKSİYON
    def manage_courses():
        ...
    """
    @wraps(f) # Bu satır, decorator'ın Flask tarafından tanınmasını sağlar
    @login_required # Önce giriş yapılmış olmasını zorunlu kıl
    def decorated_function(*args, **kwargs):
        # Eğer kullanıcı giriş yapmış ama 'Admin' DEĞİLSE:
        if not current_user.is_admin:
            # 403 Yasaklandı hatası fırlat ve işlemi durdur.
            abort(403)
        # Eğer kullanıcı Admin ise, asıl rota fonksiyonunu (f) çalıştır.
        return f(*args, **kwargs)
    return decorated_function

# --- YENİ DEKORATÖR (v6.0) ---
def staff_required(f):
    """
    Bir rotanın SADECE 'Admin' VEYA 'Personel' rolüne sahip
    (yani şirket çalışanı olan) kullanıcılar tarafından erişilebilir
    olmasını sağlayan dekoratör.
    
    Normal 'Kullanıcı' (Öğrenci) rolündekiler bu sayfaları göremez.

    Kullanım:
    @admin.route('/profile')
    @login_required
    @staff_required  <-- BU FONKSİYON
    def profile():
        ...
    """
    @wraps(f)
    @login_required # Önce giriş yapılmış olmasını zorunlu kıl
    def decorated_function(*args, **kwargs):
        # Eğer kullanıcı 'Admin' VEYA 'Personel' DEĞİLSE:
        # (models.py'ye eklediğimiz 'is_staff' metodunu kullanır)
        if not current_user.is_staff:
            # 403 Yasaklandı hatası fırlat.
            abort(403)
        # Eğer kullanıcı Admin veya Personel ise, asıl rota fonksiyonunu (f) çalıştır.
        return f(*args, **kwargs)
    return decorated_function

# NOT: Artık 3 seviyeli güvenliğimiz var:
# 1. @login_required -> Herkes (Admin, Personel, Kullanıcı) -> Akademi, Kurs Detayı
# 2. @staff_required  -> Sadece Çalışanlar (Admin, Personel) -> Profil, Satışlar
# 3. @admin_required  -> Sadece Admin (Admin) -> Kullanıcı Yönetimi, Kurs Yönetimi
