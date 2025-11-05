from extensions import db, bcrypt # bcrypt'i User modeli içinde kullanacağız
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func, CheckConstraint, event # event eklendi (şifre kontrolü için)
import hashlib # Profil fotoğrafı için gravatar URL'si oluşturmak üzere eklendi
import json # Quiz __repr__ için eklendi

# ==========================================================================
# Geliştirilmiş Veritabanı Modelleri (models.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU, PROJEMİZDEKİ EN KRİTİK GÜNCELLEMEDİR.
# "AKADEMİYİ HALKA AÇMA" HEDEFİMİZ İÇİN VERİTABANI YAPISINI GÜNCELLİYORUZ.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  YENİ ROL: "KULLANICI" (ÖĞRENCİ) ROLÜ EKLENDİ:
#     - `User` modelindeki `role` alanı artık 'Admin', 'Personel' ve
#       yeni eklenen 'Kullanıcı' rollerini kabul ediyor.
#     - `CheckConstraint` (veri bütünlüğü kuralı) bu yeni rolü
#       içerecek şekilde güncellendi.
#
# 2.  VARSAYILAN ROL GÜNCELLENDİ:
#     - `User` modelindeki `role` alanının varsayılan değeri ('default')
#       'Personel'den 'Kullanıcı'ya değiştirildi.
#     - Bu, `register.html` üzerinden kaydolan herkesin otomatik olarak
#       "Personel" değil, "Öğrenci" (Kullanıcı) olmasını sağlar.
#
# 3.  YENİ YARDIMCI METOTLAR (Properties):
#     - `@property def is_personnel(self)`: Bir kullanıcının 'Personel'
#       olup olmadığını hızlıca kontrol etmek için eklendi.
#     - `@property def is_staff(self)`: Bir kullanıcının 'Admin' VEYA
#       'Personel' olup olmadığını (yani "normal kullanıcı" olmadığını)
#       kontrol etmek için eklendi. Bu, prim/satış gibi personel
#       özelliklerini gizlemek için panelde ÇOK kullanışlı olacak.
#
# 4.  KOD TEMİZLİĞİ VE YORUM GÜNCELLEMELERİ:
#     - 'v5.0'da eklenen tüm "top seviye" özellikler (Google OAuth,
#       Gravatar, Şifre Kontrolü) korundu.
#     - Yorumlar, yeni 'v6.0' mimarisini yansıtacak şekilde güncellendi.
# ==========================================================================


# ==========================================================================
# İLİŞKİ TABLOLARI (ASSOCIATION TABLES)
# ==========================================================================
# Projeler ve Teknolojiler arasında Çoka-Çok (Many-to-Many) ilişki kurar.
project_technologies = db.Table('project_technologies',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True),
    db.Column('technology_id', db.Integer, db.ForeignKey('technology.id', ondelete='CASCADE'), primary_key=True),
    db.UniqueConstraint('project_id', 'technology_id', name='uq_project_technology')
)

# ==========================================================================
# KULLANICI MODELİ (USER) - (v6.0 GÜNCELLEMESİ)
# ==========================================================================
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    # GÜNCELLEME (v7.0): Roller: Admin, Personel, normal (küçük harf)
    __table_args__ = (
        db.CheckConstraint("role IN ('Admin', 'Personel', 'normal')", name='ck_user_role'),
    )

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True, index=True) # Google ID (v5.0)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    image_file = db.Column(db.String(200), nullable=True) # Gravatar için nullable=True (v5.0)
    password = db.Column(db.String(128), nullable=True) # Google ile kayıtta şifre olmayabilir (v5.0)
    
    # GÜNCELLEME (v7.0): Varsayılan rol 'normal' (Standart üye/müşteri) olarak ayarlandı.
    role = db.Column(db.String(20), nullable=False, default='normal', index=True)
    
    is_active = db.Column(db.Boolean, default=True, index=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Detaylı Profil Alanları (Personel ve Adminler için)
    title = db.Column(db.String(100), nullable=True) # Unvan
    quote = db.Column(db.String(250), nullable=True) # Motto
    bio = db.Column(db.Text, nullable=True) # Biyografi
    social_linkedin = db.Column(db.String(200), nullable=True)
    social_twitter = db.Column(db.String(200), nullable=True)
    social_github = db.Column(db.String(200), nullable=True)

    # İlişkiler (Bir kullanıcı silinirse, ona ait her şey silinir - cascade)
    # 'lazy='dynamic'' -> Bu ilişkilerin bir sorgu (query) olarak yüklenmesini sağlar.
    sales = db.relationship('Sale', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    activities = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """Model oluşturulurken şifre varsa otomatik hash'ler."""
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs and kwargs['password']:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        """Verilen şifreyi güvenli bir şekilde hash'ler."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verilen şifrenin hash ile eşleşip eşleşmediğini kontrol eder."""
        if not self.password: # Google ile kaydolmuş, şifresi olmayan kullanıcılar için
            return False
        return bcrypt.check_password_hash(self.password, password)

    # --- YENİ ROL KONTROL METOTLARI (v6.0) ---
    @property
    def is_admin(self):
        """Kullanıcı 'Admin' rolünde mi?"""
        return self.role == 'Admin'

    @property
    def is_personnel(self):
        """Kullanıcı 'Personel' rolünde mi?"""
        return self.role == 'Personel'

    @property
    def is_staff(self):
        """
        Kullanıcı 'Admin' VEYA 'Personel' mi?
        (Yani 'normal' değil, bir çalışan mı?)
        Bu metot, paneldeki "Satış Ekle" gibi özellikleri gizlemek için kullanılacak.
        """
        return self.role in ('Admin', 'Personel')
    
    @property
    def is_normal(self):
        """Kullanıcı 'normal' (standart üye/müşteri) rolünde mi?"""
        return self.role == 'normal'
    
    # --- YARDIMCI METOTLAR (v5.0) ---
    def avatar(self, size=100):
        """
        Profil fotoğrafı (image_file) varsa onu, yoksa varsayılan insan silüeti ikonu döndürür.
        WhatsApp'ta profil fotoğrafı olmayanlardaki gibi standart bir ikon gösterir.
        """
        from flask import url_for
        if self.image_file:
            # Resim yolu 'static/uploads/profile_pics/resim.jpg' şeklindedir
            return url_for('static', filename=f'uploads/{self.image_file}')
        else:
            # Varsayılan insan silüeti ikonu (WhatsApp stilinde)
            # Font Awesome person-circle ikonu kullanılabilir veya SVG data URI
            # Basit bir çözüm: Font Awesome ikonunu CSS ile göster
            # Alternatif: Gravatar'ın person icon seçeneği
            digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            # 'd=mp' parametresi ile varsayılan profil ikonu (monsterid veya person)
            return f'https://www.gravatar.com/avatar/{digest}?d=mp&s={size}'

    def get_total_commission(self):
        """Kullanıcının kazandığı toplam prim tutarını döndürür."""
        total = db.session.query(func.sum(Commission.amount))\
            .join(Sale)\
            .filter(Sale.user_id == self.id)\
            .scalar()
        return total or 0.0

    def get_total_sales_amount(self):
        """Kullanıcının yaptığı toplam satış miktarını döndürür."""
        total = db.session.query(func.sum(Sale.amount))\
            .filter(Sale.user_id == self.id)\
            .scalar()
        return total or 0.0

    def get_enrollment_for_course(self, course_id):
        """Kullanıcının belirli bir kursa olan kaydını döndürür."""
        return self.enrollments.filter_by(course_id=course_id).first()

    def __repr__(self):
        """Modelin terminalde nasıl görüneceğini tanımlar."""
        google_info = f", google_id='{self.google_id}'" if self.google_id else ""
        return f"<User id={self.id} username='{self.username}' role='{self.role}'{google_info}>"

# --- ŞİFRE ZORUNLULUK KONTROLÜ (v5.0) ---
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def user_check_password_if_no_google_id(mapper, connection, target):
    """
    Eğer kullanıcı Google ile kaydolmadıysa (google_id yoksa),
    şifresinin olmasını zorunlu kılar. Veri bütünlüğünü sağlar.
    """
    if not target.google_id and not target.password:
        raise ValueError("Google ID olmadan kullanıcı oluşturuluyorsa şifre zorunludur.")

# ==========================================================================
# SATIŞ & PRİM MODELLERİ (SALE, COMMISSION)
# (Değişiklik Gerekmiyor - v5.0 ile uyumlu)
# ==========================================================================
class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    # Bir personel silinirse satışları silinmesin, 'author' alanı null olsun
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True) 

    # 'author' ilişkisi (User modelinde backref ile tanımlandı)
    commission = db.relationship('Commission', backref='sale', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        author_username = self.author.username if self.author else "Silinmiş Kullanıcı"
        return f"<Sale id={self.id} user='{author_username}' amount={self.amount:.2f}>"

class Commission(db.Model):
    __tablename__ = 'commission'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    calculation_details = db.Column(db.String(500))
    is_paid = db.Column(db.Boolean, default=False, index=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    # Bir satış silinirse, primi de otomatik olarak silinsin
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id', ondelete='CASCADE'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 'sale' ilişkisi (Sale modelinde backref ile tanımlandı)

    def __repr__(self):
        paid_status = "Ödendi" if self.is_paid else "Bekliyor"
        return f"<Commission id={self.id} sale_id={self.sale_id} amount={self.amount:.2f} status='{paid_status}'>"

# ==========================================================================
# AKADEMİ MODELLERİ
# (Değişiklik Gerekmiyor - v5.0 ile uyumlu)
# ==========================================================================
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    difficulty = db.Column(db.String(20), default='Başlangıç')
    duration_hours = db.Column(db.Integer, default=0)
    cover_image = db.Column(db.String(100), nullable=True, default='course_default.png')
    instructor_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Bir kurs silinirse, tüm dersleri ve kayıtları da silinsin
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', order_by='Lesson.order', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade="all, delete-orphan")

    def get_lesson_count(self):
        """Kursa ait toplam ders sayısını döndürür."""
        return self.lessons.count()

    def get_next_lesson(self, current_lesson_order):
        """Mevcut dersten bir sonraki dersi (sıraya göre) bulur."""
        return self.lessons.filter(Lesson.order > current_lesson_order).order_by(Lesson.order.asc()).first()

    def get_prev_lesson(self, current_lesson_order):
        """Mevcut dersten bir önceki dersi (sıraya göre) bulur."""
        if current_lesson_order <= 1: return None
        return self.lessons.filter(Lesson.order < current_lesson_order).order_by(Lesson.order.desc()).first()

    def __repr__(self):
        return f"<Course id={self.id} title='{self.title}'>"

class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    lesson_type = db.Column(db.String(20), default='Video', nullable=False)
    content = db.Column(db.Text, nullable=True) # Metin dersleri veya video açıklaması
    video_url = db.Column(db.String(255), nullable=True)
    recommended_videos = db.Column(db.Text, nullable=True) # JSON array of YouTube video URLs/IDs
    order = db.Column(db.Integer, nullable=False) # Dersin kurstaki sırası
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 'course' ilişkisi (Course modelinde backref ile tanımlandı)
    # Bir ders silinirse, ona bağlı quiz de silinsin
    quiz = db.relationship('Quiz', backref='lesson', uselist=False, cascade="all, delete-orphan")

    # Bir kurs içinde aynı 'order' (sıra) numarasından sadece bir tane olabilir
    __table_args__ = (db.UniqueConstraint('course_id', 'order', name='uq_lesson_order_in_course'),)

    def __repr__(self):
        return f"<Lesson id={self.id} title='{self.title}' order={self.order}>"

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True)
    # Kullanıcı veya Kurs silinirse, bu kayıt da silinsin
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False, index=True)
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
    # Tamamlanan derslerin ID'lerini '1,5,12' gibi bir string'de saklar (v5.0)
    completed_lessons = db.Column(db.Text, default='') 

    # 'student' ve 'course' ilişkileri (User ve Course modellerinde backref ile tanımlandı)

    # Bir kullanıcı bir kursa sadece bir kez kaydolabilir
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='uq_user_course_enrollment'),)

    def get_completed_ids_set(self):
        """'1,5,12' string'ini {'1', '5', '12'} set'ine çevirir."""
        return set(filter(None, self.completed_lessons.split(','))) if self.completed_lessons else set()

    def get_progress(self):
        """Kullanıcının kurstaki ilerlemesini yüzde olarak hesaplar."""
        try:
            completed_count = len([int(id_str) for id_str in self.get_completed_ids_set()])
        except ValueError:
             completed_count = 0 
        total_lessons = self.course.get_lesson_count()
        return round((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    def add_completed_lesson(self, lesson_id):
        """Bir dersi tamamlandı listesine ekler."""
        lesson_id_str = str(lesson_id)
        completed_ids = self.get_completed_ids_set()
        if lesson_id_str not in completed_ids:
            completed_ids.add(lesson_id_str)
            try:
                # '1,12,5' -> [1, 12, 5] -> [1, 5, 12] -> '1,5,12' (Sıralı saklar)
                valid_ids = [int(id_str) for id_str in completed_ids]
                self.completed_lessons = ','.join(map(str, sorted(valid_ids)))
            except ValueError:
                 self.completed_lessons = ','.join(sorted(list(completed_ids)))

    def is_lesson_completed(self, lesson_id):
        """Belirli bir dersin tamamlanıp tamamlanmadığını kontrol eder."""
        return str(lesson_id) in self.get_completed_ids_set()

    def __repr__(self):
        return f"<Enrollment user_id={self.user_id} course_id={self.course_id} progress={self.get_progress()}%>"

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    # Bir ders silinirse, quiz de silinsin
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'), unique=True, nullable=False)
    # Soruları '[{"question": "...", "options": [...]}]' formatında JSON string olarak saklar
    questions = db.Column(db.Text, nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 'lesson' ilişkisi (Lesson modelinde backref ile tanımlandı)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        try:
            question_count = len(json.loads(self.questions))
        except:
            question_count = 0
        return f"<Quiz id={self.id} title='{self.title}' questions={question_count}>"

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'
    id = db.Column(db.Integer, primary_key=True)
    # Kullanıcı veya Quiz silinirse, bu deneme de silinsin
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 'user' ve 'quiz' ilişkileri (User ve Quiz modellerinde backref ile tanımlandı)

    @property
    def percentage(self):
        """Skoru yüzde olarak hesaplar."""
        return round((self.score / self.total_questions) * 100) if self.total_questions > 0 else 0

    def __repr__(self):
        return f"<QuizAttempt user_id={self.user_id} quiz_id={self.quiz_id} score={self.score}/{self.total_questions}>"

# ==========================================================================
# SİTE İÇİ AKTİVİTE KAYDI (ACTIVITY LOG)
# (Değişiklik Gerekmiyor - v5.0 ile uyumlu)
# ==========================================================================
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    # Kullanıcı silinirse log kalsın, sadece user_id null olsun
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(500), nullable=False)
    target_type = db.Column(db.String(50), index=True) # Örn: 'Course', 'User', 'Sale'
    target_id = db.Column(db.Integer, index=True) # Örn: Course ID'si
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # 'user' ilişkisi (User modelinde backref ile tanımlandı)

    def __repr__(self):
        user_info = f"user_id={self.user_id}" if self.user_id else "user=Silinmiş"
        target_info = f" target={self.target_type}:{self.target_id}" if self.target_type else ""
        return f"<ActivityLog {user_info} action='{self.action[:30]}...'{target_info}>"

# ==========================================================================
# VİTRİN MODELLERİ (PROJECT, TECHNOLOGY, PACKAGE, TESTIMONIAL)
# (Değişiklik Gerekmiyor - v5.0 ile uyumlu)
# ==========================================================================
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    client = db.Column(db.String(100), nullable=True)
    project_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String(255), default='project_default.png')
    live_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 'project_technologies' ilişki tablosu üzerinden
    technologies = db.relationship('Technology', secondary=project_technologies, backref='projects', lazy='dynamic')

    def __repr__(self):
        return f"<Project id={self.id} title='{self.title}'>"

class Technology(db.Model):
    __tablename__ = 'technology'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # 'projects' ilişkisi (Project modelinde backref ile tanımlandı)

    def __repr__(self):
        return f"<Technology id={self.id} name='{self.name}'>"

class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_monthly = db.Column(db.Integer, nullable=False)
    price_yearly = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    features = db.Column(db.Text, nullable=True) # Özellikler (her satıra bir özellik)
    is_popular = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0) # Paketleri sıralamak için
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_features_list(self):
        """'features' metnini '\n' karakterinden ayırarak liste olarak döndürür."""
        return [f.strip() for f in self.features.split('\n') if f.strip()] if self.features else []

    def __repr__(self):
        pop = " (Popüler)" if self.is_popular else ""
        return f"<Package id={self.id} name='{self.name}' monthly_price={self.price_monthly}{pop}>"

class Testimonial(db.Model):
    __tablename__ = 'testimonial'
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_title = db.Column(db.String(100), nullable=True)
    author_image = db.Column(db.String(200), nullable=True)
    quote = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    is_featured = db.Column(db.Boolean, default=False, index=True) # Ana sayfada öne çıkarmak için
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def get_author_avatar(self, size=80):
        """Yazar fotoğrafı yoksa rastgele bir avatar döndürür."""
        if self.author_image:
             return url_for('static', filename=f'uploads/testimonials/{self.author_image}')
        else:
             # Basitçe rastgele bir avatar veya placeholder
             digest = hashlib.md5(self.author_name.lower().encode('utf-8')).hexdigest()
             return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        feat = " (Öne Çıkan)" if self.is_featured else ""
        return f"<Testimonial id={self.id} author='{self.author_name}' rating={self.rating}{feat}>"
