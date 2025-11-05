import os
import logging
from logging.handlers import RotatingFileHandler
# ===================================================================
# GÜNCELLEME (v6.3 - Hata Düzeltmesi)
# 'secrets' kütüphanesi, 'before_request_func' içindeki 'nonce'
# oluşturucu için import edildi. Bu, 'NameError' hatasını düzeltir.
# ===================================================================
import secrets 
from flask import Flask, session, redirect, url_for, request, render_template
from config import config_by_name
from extensions import db, bcrypt, login_manager, migrate

# ===================================================================
# Geliştirilmiş Uygulama Fabrikası (app.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU DOSYA, PROJENİN KALBİDİR. TÜM MODÜLLERİ (BLUEPRINT) VE
# EKLENTİLERİ BİR ARAYA GETİREN 'create_app' FABRİKA
# FONKSİYONUNU İÇERİR.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  "AKADEMİYİ HALKA AÇMA" MİMARİSİ:
#     - 'models.py' (v6.0) içindeki 3-rollü (Admin, Personel, Kullanıcı)
#       sistemi destekler.
#     - 'auth_routes.py' (v6.1) içindeki rol bazlı yönlendirmeyi
#       destekler.
#     - 'admin_routes.py' (v6.2) içindeki '@staff_required' ve
#       '@admin_required' kilitlerini destekler.
#     - 'academy_routes.py' (v6.0) içindeki '@login_required' (herkese
#       açık akademi) mimarisini destekler.
# ===================================================================


def create_app(config_name=None):
    """
    Flask uygulamasını oluşturan ve yapılandıran ana fabrika fonksiyonu.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Loglamayı yapılandır
    configure_logging(app)
    app.logger.info(f"'{config_name}' yapılandırması ile uygulama oluşturuluyor...")

    # Eklentileri başlat
    register_extensions(app)

    # Blueprint'leri (Modülleri) kaydet
    register_blueprints(app)

    # Hata işleyicilerini (404, 500) kaydet
    register_errorhandlers(app)

    # CLI komutlarını (flask seed) kaydet
    register_commands(app)

    # Jinja filtrelerini (currency_format) kaydet
    register_template_filters(app)

    # Request handler'larını (before_request) kaydet
    register_request_handlers(app)

    app.logger.info("Kuwamedya uygulaması başarıyla başlatıldı.")
    return app

def register_extensions(app):
    """Flask eklentilerini (DB, Bcrypt, LoginManager, Migrate) başlatır."""
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) 

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Bu sayfayı görüntülemek için lütfen giriş yapın."
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User 
        return User.query.get(int(user_id))

def register_blueprints(app):
    """Uygulamanın modüllerini (Blueprint'leri) kaydeder."""
    from auth_routes import auth as auth_blueprint
    from main_routes import main as main_blueprint
    from admin_routes import admin as admin_blueprint
    from academy_routes import academy as academy_blueprint

    app.register_blueprint(auth_blueprint) 
    app.register_blueprint(main_blueprint) 
    app.register_blueprint(admin_blueprint) 
    app.register_blueprint(academy_blueprint) 
    
    app.logger.info("Blueprint'ler başarıyla kaydedildi.")


def register_errorhandlers(app):
    """Uygulama geneli için hata sayfalarını (404, 500) tanımlar."""
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Yetkisiz Erişim (403): {request.path}")
        return render_template('errors/403.html', title='Yetkiniz Yok'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.warning(f"Sayfa Bulunamadı (404): {request.path}")
        return render_template('errors/404.html', title='Sayfa Bulunamadı'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Sunucu Hatası (500): {error}", exc_info=True)
        try:
            db.session.rollback()
        except Exception as e:
            app.logger.error(f"Rollback sırasında hata: {e}")
        return render_template('errors/500.html', title='Sunucu Hatası'), 500

    app.logger.info("Hata işleyicileri başarıyla kaydedildi.")


def register_commands(app):
    """'flask seed' gibi özel terminal komutlarını ekler."""
    import click
    from flask.cli import with_appcontext
    
    @click.command('seed')
    @with_appcontext
    def seed_command():
        """Veritabanını başlangıç verileriyle doldurur."""
        from seed import seed_data 
        click.echo('Veritabanı tohumlama işlemi başlatılıyor...')
        try:
            seed_data()
            click.echo('Veritabanı başarıyla tohumlandı.')
        except Exception as e:
            click.echo(f'Tohumlama sırasında hata oluştu: {e}', err=True)
    app.cli.add_command(seed_command)

    @click.command('create-admin')
    @with_appcontext
    @click.argument('name')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin_command(name, username, email, password):
        """Komut satırından yeni bir admin kullanıcısı oluşturur."""
        from models import User
        if User.query.filter((User.email == email) | (User.username == username)).first():
            click.echo('Bu e-posta veya kullanıcı adı zaten mevcut.', err=True)
            return

        try:
            admin_user = User(name=name, username=username, email=email, password=password, role='Admin', is_active=True)
            db.session.add(admin_user)
            db.session.commit()
            click.echo(f'"{username}" adlı admin kullanıcısı başarıyla oluşturuldu.')
        except Exception as e:
            db.session.rollback()
            click.echo(f'Admin oluşturulurken hata: {e}', err=True)
    app.cli.add_command(create_admin_command)

    app.logger.info("CLI komutları başarıyla kaydedildi.")


def register_template_filters(app):
    """HTML şablonlarında kullanılacak özel Jinja filtrelerini ekler."""
    import locale
    from datetime import datetime
    
    try:
        locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')
    except locale.Error:
        app.logger.warning("Türkçe locale (tr_TR.UTF-8) ayarlanamadı. Sistem varsayılanı denenecek.")
        try:
            locale.setlocale(locale.LC_TIME, '')
        except locale.Error:
            app.logger.error("Sistem varsayılan locale ayarı da yapılamadı. Tarihler İngilizce görünebilir.")

    @app.template_filter('strftime_tr')
    def _jinja2_filter_datetime(date, fmt='%d %B %Y'):
        """Tarihleri locale'e göre formatlar. Örn: 19 Ekim 2025"""
        if not date:
            return ""
        try:
            return date.strftime(fmt)
        except Exception as e:
            app.logger.error(f"strftime_tr filtresi hatası: {e} - Tarih: {date}")
            return str(date)

    @app.template_filter('currency_format')
    def _jinja2_filter_currency(value):
        """Sayıyı Türkçe para formatında gösterir. Örn: 1.500,00 TL"""
        if value is None:
            return "0,00 TL"
        try:
            amount = float(value)
            return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
        except (ValueError, TypeError) as e:
             app.logger.error(f"currency_format filtresi hatası: {e} - Değer: {value}")
             return str(value)

    app.logger.info("Jinja filtreleri başarıyla kaydedildi.")


def register_request_handlers(app):
    """Her istek öncesi/sonrası çalışacak fonksiyonları kaydeder."""
    from flask_login import current_user

    @app.before_request
    def before_request_func():

        # Kullanıcı giriş yapmaya çalışırken gitmek istediği sayfayı kaydet
        if not current_user.is_authenticated and \
           request.endpoint and \
           not request.endpoint.startswith('static') and \
           request.endpoint not in ['auth.login', 'auth.register', 'auth.google_login', 'auth.google_callback']:
            
            session['next_url'] = request.url

    @app.context_processor
    def inject_password_form():
        """Tüm panel sayfalarında şifre değiştirme formunu kullanılabilir yapar."""
        from flask_login import current_user
        if current_user.is_authenticated:
            from forms import ChangePasswordForm
            return {'change_password_form': ChangePasswordForm()}
        return {'change_password_form': None}

    app.logger.info("Request handler'ları başarıyla kaydedildi.")


def configure_logging(app):
    """Uygulama için dosya tabanlı loglama ayarlarını yapar."""
    if app.debug or app.testing:
        logging.basicConfig(level=logging.DEBUG)
        return

    if not os.path.exists('logs'):
        try:
            os.mkdir('logs')
        except OSError as e:
            app.logger.error(f"Log klasörü oluşturulamadı: {e}")
            return

    log_file = os.path.join('logs', 'kuwamedya.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


# Bu dosya doğrudan 'python app.py' ile çalıştırılırsa:
if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('DEBUG', False))

