import os
from flask import (Blueprint, render_template, url_for, flash, redirect,
                   request, session, current_app)
from flask_login import login_user, current_user, logout_user, login_required
# ===================================================================
# Geliştirilmiş Kimlik Doğrulama Rotaları (auth_routes.py)
# Sürüm: v6.2 (Google OAuth Kaldırıldı)
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.2):
# 1.  Google OAuth KALDIRILDI:
#     - Google OAuth ile ilgili tüm kodlar kaldırıldı.
#     - configure_oauth, google_login, google_callback fonksiyonları kaldırıldı.
#     - Login formundan Google butonu kaldırıldı.
#
# 2.  V6.0 ÖZELLİKLERİ KORUNDU:
#     - Yeni 'Kullanıcı' (Öğrenci) rolü ataması (register).
#     - Rol bazlı akıllı yönlendirme (login).
# ===================================================================

# GÜNCELLEME (v6.1): 'werkzeug.urls' yerine Python'un standart 'urllib.parse' kütüphanesi
from urllib.parse import urlparse # Güvenli yönlendirme için
from extensions import db, bcrypt
from forms import RegistrationForm, LoginForm
from datetime import datetime
from utils import log_activity # Merkezi loglama fonksiyonumuzu import et

auth = Blueprint('auth', __name__, url_prefix='/auth')

# --- Geleneksel Kayıt ve Giriş Rotaları ---

@auth.route("/register", methods=['GET', 'POST'])
def register():
    """Yeni 'Kullanıcı' (Öğrenci) kaydı yapar."""
    from models import User 

    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('academy.academy_home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
                # v6.0: Rolü 'Kullanıcı' (Öğrenci) olarak atar (models.py default)
            )
            db.session.add(user)
            db.session.flush() 
            log_activity(user, f"<strong>{user.username}</strong> sisteme e-posta ile kaydoldu.")
            db.session.commit()
            login_user(user) 
            flash(f'Hoş geldin, {user.name}! Hesabın başarıyla oluşturuldu.', 'success')
            
            # v6.0: Yeni kullanıcıyı akademiye yönlendir.
            return redirect(url_for('academy.academy_home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Kayıt sırasında beklenmedik bir hata oluştu: {e}", "danger")
            current_app.logger.error(f"Kayıt hatası: {e}")

    return render_template('register.html', title='Yeni Hesap Oluştur', form=form)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    """Kullanıcı girişi yapar ve ROLÜNE GÖRE yönlendirir."""
    from models import User

    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('academy.academy_home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Hesabınız yönetici tarafından pasif hale getirilmiştir.', 'warning')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            log_activity(user, f"<strong>{user.username}</strong> sisteme e-posta ile giriş yaptı.")
            
            try:
                db.session.commit()
                
                next_page = request.args.get('next')
                
                # GÜNCELLEME (v6.1): url_parse -> urlparse
                if not next_page or urlparse(next_page).netloc != '':
                    
                    # --- ROL BAZLI YÖNLENDİRME (v6.0) ---
                    if user.is_staff:
                        next_page = url_for('admin.dashboard')
                    else:
                        next_page = url_for('academy.academy_home')
                    # --- ROL BAZLI YÖNLENDİRME SONU ---

                flash(f'Tekrar hoş geldin, {user.name}!', 'success')
                return redirect(next_page)
            except Exception as e:
                db.session.rollback()
                flash(f"Giriş sırasında bir hata oluştu: {e}", "danger")
                current_app.logger.error(f"Giriş hatası: {e}")
        else:
            flash('Giriş başarısız. E-posta veya şifrenizi kontrol edin.', 'danger')

    return render_template('login.html', title='Giriş Yap', form=form)


@auth.route("/logout")
@login_required
def logout():
    """Kullanıcı çıkışı yapar."""
    try:
        log_activity(current_user._get_current_object(), f"<strong>{current_user.username}</strong> sistemden çıkış yaptı.")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Çıkış loglanırken hata: {e}")

    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('main.home'))