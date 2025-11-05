from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, TextAreaField,
                   SelectField, FloatField, IntegerField, DateField, SelectMultipleField, widgets)
from wtforms.validators import (DataRequired, Length, Email, EqualTo, ValidationError, URL, Optional, Regexp, NumberRange)
import re
import json # QuizForm'da JSON validasyonu için

# Modelleri sadece validasyon fonksiyonları içinde import edeceğiz.
# from models import User, Technology

# ==========================================================================
# Geliştirilmiş Formlar (forms.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU DOSYA, "AKADEMİYİ HALKA AÇMA" HEDEFİMİZ DOĞRULTUSUNDA GÜNCELLENMİŞTİR.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  YENİ KULLANICI ROLÜ EKLENDİ (KRİTİK GÜNCELLEME):
#     - `models.py`'de tanımladığımız 3'lü rol yapısına (`Kullanıcı`,
#       `Personel`, `Admin`) uyum sağlamak için, 'AdminCreateUserForm' ve
#       'AdminUpdateUserForm' içindeki `role` alanının `choices`
#       (seçenekler) listesi güncellendi.
#
# 2.  GÜNCELLENEN ROL LİSTESİ:
#     - `role` alanı artık şu seçenekleri sunar:
#       [('Kullanıcı', 'Kullanıcı'), ('Personel', 'Personel'), ('Admin', 'Admin')]
#     - Bu, bir Admin'in panel üzerinden manuel olarak "Öğrenci"
#       (Kullanıcı) rolünde bir hesap oluşturabilmesini veya bir personelin
#       rolünü öğrenciye düşürebilmesini sağlar.
#
# 3.  DİĞER FORMLAR (v5.0):
#     - `RegistrationForm` (Kayıt Formu), `auth_routes.py` içinde
#       varsayılan rolü 'Kullanıcı' olarak atadığı için bu formda
#       bir değişiklik gerekmemiştir.
#     - Diğer tüm formlar (UpdateAccountForm, SaleForm, CourseForm vb.)
#       v5.0'daki gibi "kusursuz" ve "donanımlı" halleriyle korunmuştur.
# ==========================================================================


# --- Çoklu Seçim Kutusu Widget'ı (Opsiyonel - Daha iyi görünüm için) ---
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# ==========================================================================
# 1.0 - ÜYELİK FORMLARI (AUTH)
# ==========================================================================
class RegistrationForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(), Length(min=3, max=80),
        Regexp('^[a-zA-Z0-9_.]*$', message='Kullanıcı adı sadece harf, rakam, alt çizgi ve nokta içerebilir.')
    ])
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Şifreyi Doğrula', validators=[DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor.')])
    submit = SubmitField('Hesap Oluştur')

    def validate_username(self, username):
        from models import User # İçeride import
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı alınmış. Lütfen farklı bir tane seçin.')

    def validate_email(self, email):
        from models import User # İçeride import
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi ile zaten bir hesap mevcut.')

    def validate_password(self, password):
        p = password.data
        if not re.search(r'[A-Z]', p): raise ValidationError("Şifre en az bir büyük harf içermelidir.")
        if not re.search(r'[a-z]', p): raise ValidationError("Şifre en az bir küçük harf içermelidir.")
        if not re.search(r'[0-9]', p): raise ValidationError("Şifre en az bir rakam içermelidir.")

class LoginForm(FlaskForm):
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

# ==========================================================================
# 2.0 - YÖNETİM VE PROFİL FORMLARI
# ==========================================================================
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifreniz', validators=[DataRequired()])
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Yeni Şifreyi Doğrula', validators=[DataRequired(), EqualTo('new_password', message='Yeni şifreler eşleşmiyor.')])
    submit = SubmitField('Şifreyi Değiştir')

    def validate_new_password(self, new_password):
        p = new_password.data
        if not re.search(r'[A-Z]', p): raise ValidationError("Şifre en az bir büyük harf içermelidir.")
        if not re.search(r'[a-z]', p): raise ValidationError("Şifre en az bir küçük harf içermelidir.")
        if not re.search(r'[0-9]', p): raise ValidationError("Şifre en az bir rakam içermelidir.")


class AdminCreateUserForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(), Length(min=3, max=80),
        Regexp('^[a-zA-Z0-9_.]*$', message='Kullanıcı adı sadece harf, rakam, alt çizgi ve nokta içerebilir.')
    ])
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre Ata', validators=[DataRequired(), Length(min=8)])
    
    # GÜNCELLEME (v7.0): Roller: Admin, Personel, normal
    role = SelectField('Kullanıcı Rolü',
                       choices=[('normal', 'Normal (Standart Üye/Müşteri)'),
                                ('Personel', 'Personel (Çalışan)'),
                                ('Admin', 'Admin (Yönetici)')],
                       validators=[DataRequired()])
    
    title = StringField('Unvan (Opsiyonel)', validators=[Optional(), Length(max=100)])
    is_active = BooleanField('Hesap Aktif Olsun', default=True)
    submit = SubmitField('Kullanıcıyı Oluştur')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user: raise ValidationError('Bu kullanıcı adı alınmış.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user: raise ValidationError('Bu e-posta adresi ile zaten bir hesap mevcut.')


class UpdateAccountForm(FlaskForm): # Kullanıcının kendi profilini güncellemesi
    name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=80), Regexp('^[a-zA-Z0-9_.]*$', message='Kullanıcı adı geçersiz karakterler içeriyor.')])
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    picture = FileField('Profil Fotoğrafı', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Sadece resim dosyaları (jpg, png, jpeg)!')])

    title = StringField('Unvan (Örn: Web Geliştirici)', validators=[Optional(), Length(max=100)])
    quote = TextAreaField('Motto / Özlü Söz', validators=[Optional(), Length(max=250)])
    bio = TextAreaField('Hakkında', validators=[Optional(), Length(max=1000)])

    social_linkedin = StringField('LinkedIn Profil URL', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])
    social_twitter = StringField('Twitter Profil URL', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])
    social_github = StringField('GitHub Profil URL', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])

    submit = SubmitField('Profilimi Güncelle', render_kw={'name': 'submit_profile'})

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            from models import User
            user = User.query.filter_by(username=username.data).first()
            if user: raise ValidationError('Bu kullanıcı adı başkası tarafından kullanılıyor.')

    def validate_email(self, email):
        if email.data != self.original_email:
            from models import User
            user = User.query.filter_by(email=email.data).first()
            if user: raise ValidationError('Bu e-posta adresi başkası tarafından kullanılıyor.')


class AdminUpdateUserForm(UpdateAccountForm): # Adminin başka kullanıcıyı güncellemesi
    # GÜNCELLEME (v7.0): Roller: Admin, Personel, normal
    role = SelectField('Kullanıcı Rolü',
                       choices=[('normal', 'Normal (Standart Üye/Müşteri)'),
                                ('Personel', 'Personel (Çalışan)'),
                                ('Admin', 'Admin (Yönetici)')],
                       validators=[DataRequired()])
    is_active = BooleanField('Hesap Aktif')
    submit = SubmitField('Kullanıcıyı Güncelle') # Buton adı farklı


# ==========================================================================
# 3.0 - İÇERİK YÖNETİM FORMLARI (v5.0 ile aynı)
# ==========================================================================

class ProjectForm(FlaskForm):
    title = StringField('Proje Başlığı', validators=[DataRequired(), Length(max=150)])
    category = SelectField('Kategori', choices=[('Web Yazılım', 'Web Yazılım'), ('Sosyal Medya', 'Sosyal Medya'), ('Dijital Pazarlama', 'Dijital Pazarlama')], validators=[DataRequired()])
    client = StringField('Müşteri Adı', validators=[Optional(), Length(max=100)])
    project_date = DateField('Proje Bitiş Tarihi', format='%Y-%m-%d', validators=[Optional()])
    description = TextAreaField('Proje Açıklaması', validators=[Optional()])
    cover_image_url = StringField('Kapak Fotoğrafı URL', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])
    live_url = StringField('Canlı Proje Linki', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])
    technologies = SelectMultipleField('Kullanılan Teknolojiler', coerce=int, validators=[Optional()], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    submit = SubmitField('Projeyi Kaydet')


class PackageForm(FlaskForm):
    name = StringField('Paket Adı', validators=[DataRequired(), Length(max=100)])
    price_monthly = IntegerField('Aylık Fiyat (₺)', validators=[DataRequired(), NumberRange(min=0, message='Fiyat negatif olamaz.')])
    price_yearly = IntegerField('Yıllık Fiyat (₺)', validators=[DataRequired(), NumberRange(min=0, message='Fiyat negatif olamaz.')])
    description = StringField('Kısa Açıklama', validators=[Optional(), Length(max=255)])
    features = TextAreaField('Özellikler (Her satıra bir özellik yazın)', validators=[Optional()])
    is_popular = BooleanField('Popüler Paket Olarak İşaretle')
    order = IntegerField('Sıralama Önceliği', default=0, validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Paketi Kaydet')


class SaleForm(FlaskForm): # Personelin kendi profilinden eklediği form
    product_name = StringField('Satılan Ürün/Hizmet Adı', validators=[DataRequired(), Length(max=100)])
    amount = FloatField('Satış Tutarı (₺)', validators=[DataRequired(), NumberRange(min=0.01, message='Tutar sıfırdan büyük olmalıdır.')])
    submit = SubmitField('Satışı Ekle')


# ==========================================================================
# 4.0 - AKADEMİ FORMLARI (v5.0 ile aynı)
# ==========================================================================

class CourseForm(FlaskForm):
    title = StringField('Kurs Başlığı', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Kurs Açıklaması', validators=[DataRequired()])
    category = StringField('Kategori', validators=[Optional(), Length(max=50)])
    difficulty = SelectField('Zorluk Seviyesi', choices=[('Başlangıç', 'Başlangıç'), ('Orta', 'Orta'), ('İleri', 'İleri')], validators=[DataRequired()])
    duration_hours = IntegerField('Tahmini Süre (Saat)', validators=[Optional(), NumberRange(min=0)])
    instructor_name = StringField('Eğitmen Adı', validators=[Optional(), Length(max=100)])
    cover_image = FileField('Kapak Fotoğrafı', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Sadece resim dosyaları!')])
    submit = SubmitField('Kursu Kaydet')


class LessonForm(FlaskForm):
    title = StringField('Ders Başlığı', validators=[DataRequired(), Length(max=150)])
    lesson_type = SelectField('Ders Tipi', choices=[('Video', 'Video'), ('Metin', 'Metin'), ('Quiz', 'Quiz')], validators=[DataRequired()])
    content = TextAreaField('Ders İçeriği (Metin/Açıklama)', validators=[Optional()])
    video_url = StringField('Video URL (Sadece ID veya Tam URL)', validators=[Optional()])
    order = IntegerField('Ders Sırası (Örn: 1, 2, 3...)', validators=[DataRequired(), NumberRange(min=1, message='Sıra numarası 1 veya daha büyük olmalı.')])
    submit = SubmitField('Dersi Kaydet')


class QuizForm(FlaskForm):
    title = StringField('Quiz Başlığı', validators=[DataRequired(), Length(max=150)])
    questions_json = TextAreaField('Sorular (JSON Formatında)', validators=[DataRequired()])
    submit = SubmitField('Quiz Kaydet')

    def validate_questions_json(self, questions_json):
        """Girilen metnin geçerli bir JSON olup olmadığını ve temel yapıyı kontrol eder."""
        try:
            data = json.loads(questions_json.data)
            if not isinstance(data, list):
                raise ValidationError('JSON ana yapısı bir liste olmalıdır ( [...] ).')
            if not data:
                raise ValidationError('Quiz en az bir soru içermelidir.')

            for i, question in enumerate(data):
                if not isinstance(question, dict):
                    raise ValidationError(f'{i+1}. soru bir obje olmalıdır ( {{...}} ).')
                if 'question' not in question or not isinstance(question['question'], str) or not question['question']:
                    raise ValidationError(f'{i+1}. soruda geçerli bir "question" metni bulunamadı.')
                if 'options' not in question or not isinstance(question['options'], list) or len(question['options']) < 2:
                    raise ValidationError(f'{i+1}. soruda en az 2 seçenek içeren bir "options" listesi bulunamadı.')
                if 'correct_index' not in question or not isinstance(question['correct_index'], int) or not (0 <= question['correct_index'] < len(question['options'])):
                    raise ValidationError(f'{i+1}. soruda seçeneklerle uyumlu, geçerli bir "correct_index" (tam sayı) bulunamadı.')
        except json.JSONDecodeError:
            raise ValidationError('Girilen metin geçerli bir JSON formatında değil. Online JSON validator kullanabilirsiniz.')
        except ValidationError as e:
            raise e
        except Exception as e:
             raise ValidationError(f'JSON verisi işlenirken beklenmedik bir hata oluştu: {e}')
