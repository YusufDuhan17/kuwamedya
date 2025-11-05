from flask import current_app
from extensions import db
from models import Commission, Sale # ActivityLog importu kaldırıldı

# ===================================================================
# GÜNCELLEME v5.0
# 1. MERKEZİ LOGLAMA: Manuel 'ActivityLog' oluşturma işlemleri
#    kaldırıldı. Artık 'utils.py' dosyasından import edilen
#    'log_activity' fonksiyonu kullanılıyor.
# 2. TEMİZLİK: Gereksiz 'ActivityLog' importu kaldırıldı.
# 3. KORUMA: 'sale.author' kontrolü (NoneType hatasını önler)
#    korundu. Bu, mükemmel bir güvenlik önlemidir.
# ===================================================================
from utils import log_activity # Merkezi loglama fonksiyonumuzu import et

def calculate_and_record_commission(sale: Sale):
    """
    Bir satış nesnesi alarak, yapılandırmadaki orana göre primini hesaplar
    ve veritabanına yeni bir Commission nesnesi olarak kaydeder.
    Ayrıca bu işlemi ActivityLog'a kaydeder.
    """
    # --- GÜVENLİK KONTROLÜ (v3.4): NoneType hatasını önler ---
    if not sale or not sale.id:
        print(f"Prim hesaplama hatası: Geçersiz satış nesnesi alındı.")
        return False
    if not sale.author:
        print(f"Prim hesaplama hatası: Satış ID {sale.id} için kullanıcı bilgisi bulunamadı.")
        return False
    # --- GÜVENLİK KONTROLÜ SONU ---

    try:
        # Prim oranını config'den al, yoksa %10 kullan
        commission_rate = current_app.config.get('COMMISSION_RATE', 0.10)
        
        # Prim miktarını hesapla
        commission_amount = sale.amount * commission_rate
        
        # Bu satış için daha önce prim hesaplanmış mı kontrol et
        existing_commission = Commission.query.filter_by(sale_id=sale.id).first()
        if existing_commission:
            print(f"Uyarı: Satış ID {sale.id} için zaten prim hesaplanmış.")
            return False # Zaten varsa tekrar hesaplama

        new_commission = Commission(
            amount=round(commission_amount, 2),
            sale_id=sale.id,
            calculation_details=f"{sale.amount:.2f} TL tutarındaki satış için %{int(commission_rate * 100)} oranında hesaplandı."
        )
        db.session.add(new_commission)

        # GÜNCELLEME: Merkezi log_activity kullanılıyor
        log_action = f"<strong>{sale.author.username}</strong> adlı kullanıcı için <strong>{new_commission.amount:.2f} TL</strong> tutarında prim hesaplandı ({sale.product_name} satışı)."
        # 'sale.author' (User nesnesi) ve 'sale' (Sale nesnesi)
        # loglama fonksiyonuna 'target' olarak gönderiliyor.
        log_activity(sale.author, log_action, sale)
        
        # Not: Bu fonksiyon commit yapmaz!
        # Onu çağıran 'admin_routes.py' içindeki 'new_sale' rotası
        # 'db.session.commit()' yaparak hem satışı hem de primi
        # aynı anda veritabanına işler (Bu, 'atomik' işlem için en doğrusudur).
        print(f"Başarılı: Satış ID {sale.id} için {new_commission.amount:.2f} TL prim eklendi.")
        return True

    except Exception as e:
        import traceback
        print(f"Prim hesaplama sırasında beklenmedik bir hata oluştu: {e}")
        print(traceback.format_exc())
        db.session.rollback() # Hata olursa işlemi geri al
        return False
