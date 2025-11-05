import os
import secrets
import json
from PIL import Image
from flask import (Blueprint, render_template, url_for, flash, redirect,
                   request, abort, current_app)
from flask_login import current_user, login_required
from extensions import db, bcrypt
from utils import log_activity, save_picture
from decorators import admin_required, staff_required

# Tarih/Zaman ve Veritabanı Fonksiyonları
from datetime import datetime, date
# ===================================================================
# GÜNCELLEME (v6.2 - Hata Düzeltmesi)
# "relativedelativedelta" yazım hatası düzeltildi.
# ===================================================================
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract, desc

admin = Blueprint('admin', __name__, url_prefix='/admin')

# ==========================================================================
# 1.0 - ANA PANEL VE DASHBOARD ROTALARI
# ==========================================================================

@admin.route("/")
@admin.route("/dashboard")
@login_required
def dashboard():
    """
    Giriş yapan kullanıcıyı rolüne göre doğru panele yönlendirir. (v6.0)
    Admin -> /admin_dashboard
    Personel -> /profile
    Kullanıcı -> (Akademiye yönlendir)
    """
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    elif current_user.is_staff: # Sadece Personel (Admin değil)
        return redirect(url_for('admin.profile'))
    else:
        # Buraya bir 'Kullanıcı' (Öğrenci) gelirse (URL'yi manuel yazarsa)
        # onu ait olduğu akademiye geri yolla.
        flash("Bu alana erişim yetkiniz bulunmuyor.", "warning")
        return redirect(url_for('academy.academy_home'))

@admin.route("/admin_dashboard")
@admin_required # SADECE Admin görebilir
def admin_dashboard():
    """Yöneticinin göreceği, tüm istatistikleri içeren ana kontrol paneli."""
    from models import User, Sale, Commission, Course, ActivityLog

    try:
        today = date.today()
        start_of_month = today.replace(day=1)

        # is_staff bir property olduğu için SQL sorgusunda kullanılamaz, role kullanmalıyız
        total_personnel = User.query.filter(User.role == 'Personel').count() # v6.2
        total_admins = User.query.filter_by(role='Admin').count() # v6.2
        total_users = User.query.filter_by(role='normal').count() # v7.0
        monthly_revenue = db.session.query(func.coalesce(func.sum(Sale.amount), 0.0)).filter(Sale.date_posted >= start_of_month).scalar()
        monthly_commission = db.session.query(func.coalesce(func.sum(Commission.amount), 0.0)).join(Sale).filter(Sale.date_posted >= start_of_month).scalar()
        active_courses = Course.query.count()

        recent_activities = ActivityLog.query.order_by(desc(ActivityLog.timestamp)).limit(5).all()
        # v6.2: En yeni personelleri göster (Personel ve Admin) - is_staff property olduğu için role kullanıyoruz
        latest_users = User.query.filter(User.role.in_(['Admin', 'Personel'])).order_by(desc(User.date_created)).limit(5).all()

        stats = {
            'total_staff': total_personnel + total_admins, # v6.2 (Personel + Admin)
            'total_users': total_users, # v6.0 (Sadece Öğrenciler)
            'monthly_revenue': monthly_revenue,
            'monthly_commission': monthly_commission,
            'active_courses': active_courses,
        }
    except Exception as e:
        current_app.logger.error(f"Admin dashboard verileri çekilirken hata: {e}")
        flash("Dashboard verileri yüklenirken bir hata oluştu.", "danger")
        stats = {}
        latest_users = []
        recent_activities = []

    return render_template('admin/admin_dashboard.html',
                           title='Yönetici Paneli',
                           stats=stats,
                           latest_users=latest_users,
                           recent_activities=recent_activities)

# ==========================================================================
# 2.0 - PERSONEL YÖNETİMİ (CRUD - SADECE ADMİN)
# ==========================================================================

@admin.route("/user_list")
@admin_required # SADECE Admin görebilir
def user_list():
    """Sadece personelleri (Admin ve Personel) sayfalayarak listeler."""
    from models import User

    page = request.args.get('page', 1, type=int)
    try:
        # Sadece Admin ve Personel rollerini listele (normal kullanıcıları gösterme)
        users = User.query.filter(User.role.in_(['Admin', 'Personel'])).order_by(desc(User.date_created)).paginate(page=page, per_page=10, error_out=False)
    except Exception as e:
        current_app.logger.error(f"Kullanıcı listesi alınırken hata: {e}")
        flash("Kullanıcı listesi yüklenirken bir hata oluştu.", "danger")
        users = None

    return render_template('admin/list_users.html', title='Kullanıcı Yönetimi', users=users)

@admin.route("/add_user", methods=['GET', 'POST'])
@admin_required # SADECE Admin görebilir
def add_user():
    """Yönetici için yeni personel/kullanıcı ekleme sayfası."""
    from models import User
    from forms import AdminCreateUserForm

    form = AdminCreateUserForm()
    if form.validate_on_submit():
        try:
            user = User(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data, 
                role=form.role.data, # v6.0: Formdan 'Kullanıcı' rolü de seçilebilir
                is_active=form.is_active.data,
                title=form.title.data
            )
            db.session.add(user)
            db.session.flush()
            log_activity(current_user._get_current_object(), f"yeni bir kullanıcı ({user.role}) oluşturdu: <strong>{user.username}</strong>", user)
            db.session.commit()
            flash(f'"{user.name}" adlı kullanıcı başarıyla oluşturuldu!', 'success')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni kullanıcı eklenirken hata: {e}")
            flash(f"Kullanıcı eklenirken bir hata oluştu: {e}", "danger")

    return render_template('admin/edit_user.html', title='Yeni Kullanıcı Ekle', form=form, user=None)

@admin.route("/edit_user/<int:user_id>", methods=['GET', 'POST'])
@admin_required # SADECE Admin görebilir
def edit_user(user_id):
    """Yöneticinin bir kullanıcının bilgilerini düzenlediği sayfa."""
    from models import User
    from forms import AdminUpdateUserForm

    user_to_edit = User.query.get_or_404(user_id)
    form = AdminUpdateUserForm(obj=user_to_edit, original_username=user_to_edit.username, original_email=user_to_edit.email)
    
    current_image = user_to_edit.image_file

    if form.validate_on_submit():
        try:
            form.populate_obj(user_to_edit)
            
            # Şifre değiştirme (admin için - mevcut şifre gerektirmez)
            if form.new_password.data:
                user_to_edit.set_password(form.new_password.data)
            
            if form.picture.data:
                try:
                    picture_file = save_picture(form.picture.data, folder='profile_pics', output_size=(300, 300))
                    user_to_edit.image_file = picture_file
                except ValueError as ve: 
                     flash(str(ve), 'danger')
                     return redirect(url_for('admin.edit_user', user_id=user_id))
            else:
                user_to_edit.image_file = current_image 

            log_activity(current_user._get_current_object(), f"<strong>{user_to_edit.username}</strong> adlı kullanıcının bilgilerini güncelledi.", user_to_edit)
            db.session.commit()
            if form.new_password.data:
                flash(f'"{user_to_edit.name}" adlı kullanıcının bilgileri ve şifresi güncellendi.', 'success')
            else:
                flash(f'"{user_to_edit.name}" adlı kullanıcının bilgileri güncellendi.', 'success')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kullanıcı {user_id} düzenlenirken hata: {e}")
            flash(f"Kullanıcı bilgileri güncellenirken bir hata oluştu: {e}", "danger")

    # v6.0: Formu da gönderiyoruz (AdminUpdateUserForm)
    return render_template('admin/edit_user.html', title=f"Düzenle: {user_to_edit.name}", form=form, user=user_to_edit)


@admin.route("/delete_user/<int:user_id>", methods=['POST'])
@admin_required # SADECE Admin görebilir
def delete_user(user_id):
    """Bir kullanıcıyı sistemden kalıcı olarak siler."""
    from models import User

    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash('Kendinizi silemezsiniz.', 'danger')
        return redirect(url_for('admin.user_list'))

    try:
        username = user_to_delete.username
        db.session.delete(user_to_delete)
        log_activity(current_user._get_current_object(), f"<strong>{username}</strong> adlı kullanıcıyı sistemden sildi.")
        db.session.commit()
        flash(f'"{username}" adlı kullanıcı başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Kullanıcı {user_id} silinirken hata: {e}")
        flash(f"Kullanıcı silinirken bir hata oluştu: {e}", "danger")

    return redirect(url_for('admin.user_list'))

# ==========================================================================
# 3.0 - PROFİL SAYFALARI
# ==========================================================================

def get_monthly_sales_data(user_id):
    """(Yardımcı Fonksiyon) Belirli bir kullanıcı için son 6 aylık satış verisini Chart.js formatında döndürür."""
    from models import Sale

    today = date.today()
    labels = []
    data = []
    
    try:
        for i in range(5, -1, -1):
            month_start = (today - relativedelta(months=i)).replace(day=1)
            month_end = month_start + relativedelta(months=1)
            month_name = month_start.strftime("%B") 
            labels.append(month_name)

            monthly_sale = db.session.query(func.coalesce(func.sum(Sale.amount), 0.0))\
                .filter(Sale.user_id == user_id,
                        Sale.date_posted >= month_start,
                        Sale.date_posted < month_end)\
                .scalar()
            data.append(monthly_sale)
    except Exception as e:
         current_app.logger.error(f"Aylık satış verisi alınırken hata (user_id={user_id}): {e}")
         return {"labels": ["Hata"]*6, "data": [0]*6}

    return {"labels": labels, "data": data}

@admin.route("/profile", methods=['GET', 'POST'])
@login_required # v6.0: Artık tüm roller (Kullanıcı, Personel, Admin) kendi profilini görebilir
def profile():
    """Giriş yapmış kullanıcının kendi kişisel profil sayfası."""
    from models import User, Sale, Enrollment
    from forms import UpdateAccountForm, ChangePasswordForm, SaleForm

    user = current_user
    update_form = UpdateAccountForm(obj=user, original_username=user.username, original_email=user.email)
    password_form = ChangePasswordForm()
    sale_form = SaleForm()
    
    current_image = user.image_file

    # Profil Güncelleme Formu (POST)
    if update_form.validate_on_submit() and 'submit_profile' in request.form:
        try:
            update_form.populate_obj(user)
            
            if update_form.picture.data:
                try:
                    picture_file = save_picture(update_form.picture.data, folder='profile_pics', output_size=(300, 300))
                    user.image_file = picture_file
                except ValueError as ve:
                     flash(str(ve), 'danger')
                     return redirect(url_for('admin.profile'))
            else:
                user.image_file = current_image

            log_activity(user, "profilini güncelledi.")
            db.session.commit()
            flash('Profiliniz başarıyla güncellendi!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profil güncellenirken hata (user_id={user.id}): {e}")
            flash(f"Profil güncellenirken bir hata oluştu: {e}", "danger")
        return redirect(url_for('admin.profile'))

    # Şifre Değiştirme Formu (POST)
    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if user.check_password(password_form.current_password.data):
            try:
                user.set_password(password_form.new_password.data)
                log_activity(user, "şifresini değiştirdi.")
                db.session.commit()
                flash('Şifreniz başarıyla değiştirildi!', 'success')
            except Exception as e:
                 db.session.rollback()
                 current_app.logger.error(f"Şifre değiştirilirken hata (user_id={user.id}): {e}")
                 flash(f"Şifre değiştirilirken bir hata oluştu: {e}", "danger")
        else:
            flash('Mevcut şifreniz hatalı.', 'danger')
        return redirect(url_for('admin.profile'))

    # --- GET isteği ---
    try:
        # v6.0: Sadece 'staff' (çalışan) ise satış/prim verilerini çek.
        if user.is_staff:
            sales_page = request.args.get('sales_page', 1, type=int)
            sales_pagination = Sale.query.filter_by(author=user).order_by(desc(Sale.date_posted)).paginate(page=page, per_page=5, error_out=False)
            total_sales_amount = user.get_total_sales_amount()
            total_commission = user.get_total_commission()
            monthly_sales_json = json.dumps(get_monthly_sales_data(user.id))
        else:
            sales_pagination, total_sales_amount, total_commission, monthly_sales_json = None, 0.0, 0.0, json.dumps({"labels": [], "data": []})

        # Akademi verileri herkes için çekilebilir
        enrollments = user.enrollments.order_by(Enrollment.date_enrolled.desc()).all()
        completed_courses_count = sum(1 for en in enrollments if en.get_progress() == 100)
        
    except Exception as e:
         current_app.logger.error(f"Profil sayfası verileri çekilirken hata (user_id={user.id}): {e}")
         flash("Profil verileri yüklenirken bir hata oluştu.", "danger")
         sales_pagination, total_sales_amount, total_commission, enrollments, completed_courses_count, monthly_sales_json = None, 0.0, 0.0, [], 0, json.dumps({"labels": [], "data": []})

    # v6.0: profile.html şablonu artık 'user.is_staff' kontrolü yapıyor.
    return render_template('panel/profile.html', title=f'{user.name} | Profilim',
                           user=user,
                           update_form=update_form,
                           password_form=password_form,
                           sale_form=sale_form,
                           sales=sales_pagination,
                           total_sales_amount=total_sales_amount,
                           total_commission=total_commission,
                           enrollments=enrollments,
                           completed_courses_count=completed_courses_count,
                           monthly_sales_data=monthly_sales_json)


@admin.route("/profile/<string:username>")
@admin_required # SADECE Admin görebilir
def view_user_profile(username):
    """Adminin başka bir kullanıcının profilini görüntülemesi."""
    from models import User, Sale, Enrollment

    user = User.query.filter_by(username=username).first_or_404()

    try:
        if user.is_staff:
            sales_page = request.args.get('sales_page', 1, type=int)
            sales_pagination = Sale.query.filter_by(author=user).order_by(desc(Sale.date_posted)).paginate(page=sales_page, per_page=5, error_out=False)
            total_sales_amount = user.get_total_sales_amount()
            total_commission = user.get_total_commission()
            monthly_sales_json = json.dumps(get_monthly_sales_data(user.id))
        else:
            sales_pagination, total_sales_amount, total_commission, monthly_sales_json = None, 0.0, 0.0, json.dumps({"labels": [], "data": []})

        enrollments = user.enrollments.order_by(Enrollment.date_enrolled.desc()).all()
        completed_courses_count = sum(1 for en in enrollments if en.get_progress() == 100)
        
    except Exception as e:
        current_app.logger.error(f"Başkasının profili görüntülenirken hata (username={username}): {e}")
        flash("Profil verileri yüklenirken bir hata oluştu.", "danger")
        sales_pagination, total_sales_amount, total_commission, enrollments, completed_courses_count, monthly_sales_json = None, 0.0, 0.0, [], 0, json.dumps({"labels": [], "data": []})

    return render_template('panel/profile.html', title=f"{user.name} Profili",
                           user=user,
                           update_form=None, 
                           password_form=None,
                           sale_form=None,
                           sales=sales_pagination,
                           total_sales_amount=total_sales_amount,
                           total_commission=total_commission,
                           enrollments=enrollments,
                           completed_courses_count=completed_courses_count,
                           monthly_sales_data=monthly_sales_json)

# ==========================================================================
# 4.0 - SATIŞ YÖNETİMİ
# ==========================================================================

@admin.route("/new_sale", methods=['POST'])
@staff_required # v6.0: SADECE Admin veya Personel satış ekleyebilir.
def new_sale():
    """Personelin (veya Adminin) kendisi için yeni bir satış eklemesini sağlar (Modal'dan çağrılır)."""
    from models import Sale
    from forms import SaleForm
    from commission_engine import calculate_and_record_commission

    form = SaleForm()
    if form.validate_on_submit():
        try:
            sale = Sale(product_name=form.product_name.data,
                        amount=form.amount.data,
                        author=current_user._get_current_object())
            db.session.add(sale)
            db.session.flush()

            log_action = f"yeni bir satış ekledi: <strong>{sale.product_name}</strong> tutarında ₺{sale.amount:.2f}"
            log_activity(current_user._get_current_object(), log_action, sale)

            commission_success = calculate_and_record_commission(sale)
            db.session.commit()

            if commission_success:
                flash('Satış başarıyla eklendi ve prim hesaplandı!', 'success')
            else:
                flash('Satış eklendi ancak prim hesaplanırken bir sorun oluştu.', 'warning')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni satış eklenirken hata (user_id={current_user.id}): {e}")
            flash(f"Satış eklenirken beklenmedik bir hata oluştu: {e}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('admin.profile')) 


# ==========================================================================
# 5.0 - İÇERİK YÖNETİMİ (PROJE, PAKET - SADECE ADMİN)
# ==========================================================================
# Bu rotaların hepsi v5.0'da olduğu gibi @admin_required olarak kalmalıdır.

@admin.route("/project_list")
@admin_required
def project_list():
    from models import Project
    try:
        projects = Project.query.order_by(desc(Project.project_date)).all()
    except Exception as e:
        current_app.logger.error(f"Projeler listelenirken hata: {e}")
        flash("Projeler yüklenirken bir hata oluştu.", "danger")
        projects = []
        
    return render_template('admin/list_projects.html', title='Proje Yönetimi', projects=projects)

@admin.route("/add_project", methods=['GET', 'POST'])
@admin_required
def add_project():
    from models import Project, Technology
    from forms import ProjectForm

    form = ProjectForm()
    if hasattr(form, 'technologies'):
         form.technologies.choices = [(t.id, t.name) for t in Technology.query.order_by('name').all()]

    if form.validate_on_submit():
        try:
            new_project = Project(
                title=form.title.data,
                category=form.category.data,
                client=form.client.data,
                project_date=form.project_date.data,
                description=form.description.data,
                cover_image_url=form.cover_image_url.data,
                live_url=form.live_url.data
            )
            if hasattr(form, 'technologies'):
                selected_techs = Technology.query.filter(Technology.id.in_(form.technologies.data)).all()
                new_project.technologies = selected_techs

            db.session.add(new_project)
            db.session.flush()
            log_activity(current_user._get_current_object(), f"yeni bir proje ekledi: <strong>{new_project.title}</strong>", new_project)
            db.session.commit()
            flash('Proje başarıyla eklendi!', 'success')
            return redirect(url_for('admin.project_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni proje eklenirken hata: {e}")
            flash(f"Proje eklenirken bir hata oluştu: {e}", "danger")

    return render_template('admin/create_edit_project.html', title='Yeni Proje Ekle', form=form, project=None)

@admin.route("/edit_project/<int:project_id>", methods=['GET', 'POST'])
@admin_required
def edit_project(project_id):
    from models import Project, Technology
    from forms import ProjectForm

    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if hasattr(form, 'technologies'):
        form.technologies.choices = [(t.id, t.name) for t in Technology.query.order_by('name').all()]

    if form.validate_on_submit():
        try:
            # Technologies verisini önce al (populate_obj'den önce)
            technologies_data = None
            if hasattr(form, 'technologies'):
                technologies_data = form.technologies.data if form.technologies.data else []
            
            # Form verilerini projeye manuel olarak aktar (populate_obj many-to-many ilişkileri handle edemez)
            project.title = form.title.data
            project.category = form.category.data
            project.client = form.client.data
            project.project_date = form.project_date.data
            project.description = form.description.data
            project.cover_image_url = form.cover_image_url.data
            project.live_url = form.live_url.data
            
            # Technologies'i manuel olarak ayarla
            if technologies_data and isinstance(technologies_data, list) and len(technologies_data) > 0:
                # Integer ID'leri kontrol et ve filtrele
                tech_ids = []
                for tid in technologies_data:
                    try:
                        if isinstance(tid, int):
                            tech_ids.append(tid)
                        elif isinstance(tid, str) and tid.isdigit():
                            tech_ids.append(int(tid))
                    except (ValueError, TypeError):
                        continue
                
                if tech_ids:
                    selected_techs = Technology.query.filter(Technology.id.in_(tech_ids)).all()
                    project.technologies = selected_techs
                else:
                    project.technologies = []
            else:
                project.technologies = []

            log_activity(current_user._get_current_object(), f"<strong>{project.title}</strong> projesini güncelledi.", project)
            db.session.commit()
            flash('Proje başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.project_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Proje {project_id} güncellenirken hata: {e}")
            flash(f"Proje güncellenirken bir hata oluştu: {e}", "danger")
    elif request.method == 'GET' and hasattr(form, 'technologies'):
        form.technologies.data = [t.id for t in project.technologies]

    return render_template('admin/create_edit_project.html', title='Projeyi Düzenle', form=form, project=project)

@admin.route("/delete_project/<int:project_id>", methods=['POST'])
@admin_required
def delete_project(project_id):
    from models import Project
    project = Project.query.get_or_404(project_id)
    try:
        title = project.title
        db.session.delete(project)
        log_activity(current_user._get_current_object(), f"<strong>{title}</strong> projesini sildi.")
        db.session.commit()
        flash(f'"{title}" projesi başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Proje {project_id} silinirken hata: {e}")
        flash(f"Proje silinirken bir hata oluştu: {e}", "danger")
    return redirect(url_for('admin.project_list'))

# --- Paket Yönetimi ---
@admin.route("/package_list")
@admin_required
def package_list():
    from models import Package
    try:
        packages = Package.query.order_by(Package.order, Package.price_monthly).all()
    except Exception as e:
        current_app.logger.error(f"Paketler listelenirken hata: {e}")
        flash("Paketler yüklenirken bir hata oluştu.", "danger")
        packages = []
        
    return render_template('admin/list_packages.html', title='Paket Yönetimi', packages=packages)

@admin.route("/add_package", methods=['GET', 'POST'])
@admin_required
def add_package():
    from models import Package
    from forms import PackageForm
    form = PackageForm()
    if form.validate_on_submit():
        try:
            package = Package()
            form.populate_obj(package)
            db.session.add(package)
            db.session.flush()
            log_activity(current_user._get_current_object(), f"yeni bir paket ekledi: <strong>{package.name}</strong>", package)
            db.session.commit()
            flash('Paket başarıyla eklendi!', 'success')
            return redirect(url_for('admin.package_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni paket eklenirken hata: {e}")
            flash(f"Paket eklenirken bir hata oluştu: {e}", "danger")
            
    return render_template('admin/create_edit_package.html', title='Yeni Paket Ekle', form=form, package=None)

@admin.route("/edit_package/<int:package_id>", methods=['GET', 'POST'])
@admin_required
def edit_package(package_id):
    from models import Package
    from forms import PackageForm
    package = Package.query.get_or_404(package_id)
    form = PackageForm(obj=package)
    if form.validate_on_submit():
        try:
            form.populate_obj(package)
            log_activity(current_user._get_current_object(), f"<strong>{package.name}</strong> paketini güncelledi.", package)
            db.session.commit()
            flash('Paket başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.package_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Paket {package_id} güncellenirken hata: {e}")
            flash(f"Paket güncellenirken bir hata oluştu: {e}", "danger")
            
    return render_template('admin/create_edit_package.html', title='Paketi Düzenle', form=form, package=package)

@admin.route("/delete_package/<int:package_id>", methods=['POST'])
@admin_required
def delete_package(package_id):
    from models import Package
    package = Package.query.get_or_404(package_id)
    try:
        name = package.name
        db.session.delete(package)
        log_activity(current_user._get_current_object(), f"<strong>{name}</strong> paketini sildi.")
        db.session.commit()
        flash(f'"{name}" paketi başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Paket {package_id} silinirken hata: {e}")
        flash(f"Paket silinirken bir hata oluştu: {e}", "danger")
    return redirect(url_for('admin.package_list'))