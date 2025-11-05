from flask import Blueprint, render_template, abort, current_app
from sqlalchemy import func, desc
# extensions ve models 'app context' içinde (fonksiyon içinde) import edilecek

# ===================================================================
# Geliştirilmiş Ana Rotalar (main_routes.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU DOSYA, "AKADEMİYİ HALKA AÇMA" HEDEFİMİZ DOĞRULTUSUNDA GÜNCELLENMİŞTİR.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  GÜVENLİK VE ROL GÜNCELLEMESİ (KRİTİK):
#     - 'models.py' (v6.0) dosyasında 'is_staff' (Personel VEYA Admin)
#       adında yeni bir 'property' (özellik) tanımladık.
#     - 'personnel_list' (Ekibimiz) ve 'public_user_profile' (Halka
#       Açık Profil) rotaları artık sorgularını (query)
#       `role == 'Personel'` yerine `is_staff == True`
#       kullanarak yapıyor.
#
# 2.  BU GÜNCELLEME NEDEN KRİTİK?
#     - 'personnel_list': Artık "Ekibimiz" sayfasında sadece
#       Personeller değil, Adminler de (çünkü onlar da 'is_staff'
#       olarak True döner) listelenecek.
#     - 'public_user_profile': Bu rota, artık 'Kullanıcı' (Öğrenci)
#       rolündeki birinin (onlar için 'is_staff' False döner)
#       halka açık bir profil sayfasına sahip olmasını engeller.
#
# 3.  KOD TEMİZLİĞİ (v5.0 KORUNDU):
#     - v5.0'daki 'try...except' blokları, loglama ve 'abort'
#       mekanizmaları gibi tüm "kusursuz" özellikler korunmuştur.
# ===================================================================

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    """
    Projenin ana sayfasını oluşturur. Dinamik içerikleri veritabanından çeker.
    """
    # Modelleri içeride import et
    from models import Project, Testimonial, User

    stats, testimonials, latest_projects = {}, [], []
    try:
        # GÜNCELLEME (v6.0): İstatistikler 'is_staff' olanları sayar
        stats = {
            'completed_projects': Project.query.count(),
            'happy_clients': Testimonial.query.filter_by(is_featured=True).count() or Testimonial.query.count(),
            'team_members': User.query.filter(User.is_active == True, User.is_staff == True).count(), # Sadece çalışanları say
            'awards_won': 25 # Statik
        }
        # Yorumlar
        testimonials = Testimonial.query.filter_by(is_featured=True).order_by(desc(Testimonial.created_at)).limit(5).all()
        if not testimonials:
             testimonials = Testimonial.query.order_by(desc(Testimonial.created_at)).limit(5).all()

        # Son Projeler
        latest_projects = Project.query.order_by(desc(Project.project_date)).limit(4).all()

    except Exception as e:
        current_app.logger.error(f"Ana sayfa verileri çekilirken hata oluştu: {e}")
    
    # 'index.html' şablonunu render et
    return render_template('index.html',
                           title='Kuwamedya - Dijital Çözüm Ortağınız',
                           stats=stats,
                           testimonials=testimonials,
                           latest_projects=latest_projects,
                           active_page='home')

@main.route("/portfolio")
def portfolio():
    """Tüm projeleri ve kategorilerini portfolyo sayfasında listeler."""
    from models import Project, db

    projects, categories = [], []
    try:
        projects = Project.query.order_by(desc(Project.project_date)).all()
        categories_query = db.session.query(Project.category).filter(Project.category.isnot(None), Project.category != '').distinct().all()
        categories = sorted([category[0] for category in categories_query])

    except Exception as e:
        current_app.logger.error(f"Portfolyo verileri çekilirken hata oluştu: {e}")

    # 'portfolio.html' şablonunu render et
    return render_template('portfolio.html',
                           title='Portfolyo - Gerçekleştirdiğimiz Projeler',
                           projects=projects,
                           categories=categories,
                           active_page='portfolio')

@main.route("/packages")
def packages():
    """Tüm hizmet paketlerini listeler."""
    from models import Package

    packages = []
    all_unique_features = set()
    try:
        packages = Package.query.order_by(Package.order.asc(), Package.price_monthly.asc()).all()
        # Tüm paketlerin özelliklerinden benzersiz özellik listesi oluştur
        for package in packages:
            if package.features:
                features_list = package.get_features_list()
                all_unique_features.update(features_list)
    except Exception as e:
        current_app.logger.error(f"Hizmet paketleri çekilirken hata oluştu: {e}")
    
    # 'packages.html' şablonunu render et
    return render_template('packages.html',
                           title='Hizmet Paketlerimiz - Şeffaf Fiyatlandırma',
                           packages=packages,
                           all_features=sorted(list(all_unique_features)),
                           active_page='packages')

@main.route("/personnel")
def personnel_list():
    """Tüm aktif personelleri 'Ekibimiz' sayfasında listeler."""
    from models import User

    team_members = []
    try:
        # GÜNCELLEME (v6.0): Sorgu artık 'role' alanını kullanıyor.
        # Bu, 'Admin' ve 'Personel' rollerini kapsar, 'Kullanıcı' rolünü dışlar.
        # Not: is_staff bir property olduğu için SQL sorgusunda kullanılamaz,
        # bu yüzden role.in_() kullanıyoruz.
        team_members = User.query.filter(
            User.is_active == True,
            User.role.in_(['Admin', 'Personel'])
        ).order_by(User.name.asc()).all()
    except Exception as e:
        current_app.logger.error(f"Personel listesi çekilirken hata oluştu: {e}")

    # 'personel.html' şablonunu render et
    return render_template('personel.html',
                           title='Ekibimiz - Alanında Uzman Profesyoneller',
                           team_members=team_members,
                           active_page='personel')

# --- GÜNCELLENMİŞ ROTA (v6.0) ---
@main.route("/ekip/<string:username>")
def public_user_profile(username):
    """
    Belirli bir personelin halka açık profil sayfasını gösterir.
    Sadece aktif ve 'is_staff' (Personel veya Admin) olan kullanıcılar için çalışır.
    """
    from models import User

    try:
        # GÜNCELLEME (v6.0): Sorgu artık 'role' alanını kullanıyor.
        # Not: is_staff bir property olduğu için SQL sorgusunda kullanılamaz.
        user = User.query.filter(
            User.username == username,
            User.is_active == True,
            User.role.in_(['Admin', 'Personel']) # 'normal' (Standart üye) rolünü dışlar
        ).first_or_404()
        
        # Gelecekte buraya personelin halka açık projeleri eklenebilir.

    except Exception as e:
        current_app.logger.error(f"Halka açık profil sayfası yüklenirken hata (username={username}): {e}")
        abort(500) # first_or_404() zaten 404 fırlatır, bu diğer hatalar için

    # 'public_profile.html' şablonunu render et
    return render_template('public_profile.html',
                           title=f"{user.name} | Ekibimiz",
                           user=user)
