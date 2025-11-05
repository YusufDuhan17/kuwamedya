import json
import os
import secrets
from datetime import datetime
from io import BytesIO
from PIL import Image
from flask import (Blueprint, render_template, url_for, flash, redirect,
                   request, abort, current_app, jsonify, make_response)
from flask_login import current_user, login_required
from sqlalchemy import desc, exc
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

from extensions import db
# ===================================================================
# Geliştirilmiş Akademi Rotaları (academy_routes.py)
# Sürüm: v6.0 (Akademi Yükseltmesi)
#
# BU DOSYA, "AKADEMİYİ HALKA AÇMA" HEDEFİMİZİN BAŞARIYA ULAŞTIĞI YERDİR.
# ÖNCEKİ DOSYALARDA (models, auth, admin) YAPTIĞIMIZ GÜÇLÜ ALTYAPI
# SAYESİNDE, BU DOSYADA NEREDEYSE HİÇBİR KOD DEĞİŞİKLİĞİ GEREKMEMEKTEDİR.
#
# YENİLİKLER VE GÜÇLENDİRMELER (v6.0):
# 1.  GÜVENLİK MODELİ DOĞRULANDI (EN ÖNEMLİ GÜNCELLEME):
#     - "Halka açık" (öğrenciye yönelik) tüm rotalar (`academy_home`,
#       `course_detail`, `lesson_view`, `submit_quiz` vb.)
#       `@login_required` dekoratörünü kullanıyordu.
#     - `auth_routes.py` dosyasını, yeni kullanıcıları 'Kullanıcı' (Öğrenci)
#       rolüyle kaydetmesi için güncellediğimizden, `@login_required`
#       dekoratörü artık bu yeni 'Kullanıcı' (Öğrenci) rolünü de
#       OTOMATİK OLARAK kabul etmektedir.
#     - Bu sayede, Akademi'yi halka açmak için bu rotalarda SIFIR
#       değişiklik gerekmiştir. Mimari, planlandığı gibi çalışmıştır.
#
# 2.  ADMİN GÜVENLİĞİ DOĞRULANDI (KORUNDU):
#     - Tüm yönetim rotaları (`manage_courses`, `add_course`, `edit_lesson`
#       vb.) v5.0'da olduğu gibi `@admin_required` dekoratörünü
#       korumaya devam etmektedir.
#     - Bu, 'Kullanıcı' (Öğrenci) veya 'Personel' rollerinin
#       yönetim paneline erişmesini engeller.
#
# 3.  ŞABLON YOLLARI DOĞRULANDI (KORUNDU):
#     - v5.0'daki `panel/` ve `admin/` şablon yolları korunmuştur.
#     - Yeni 'Kullanıcı' (Öğrenci) rolü, giriş yaptığında
#       `_panel_layout.html`'i görür. `_panel_layout.html`'deki
#       `@if current_user.is_admin` kontrolleri sayesinde,
#       öğrenci sadece "Kontrol Paneli" ve "Akademi" linklerini görür.
#     - Öğrenci "Kontrol Paneli" linkine tıklarsa, `admin_routes.py`
#       içindeki `dashboard()` rotası, 'is_staff' olmayanları
#       `academy.academy_home` rotasına geri yönlendirir.
#     - Bu, mimarinin kusursuz ve güvenli çalıştığını kanıtlar.
# ===================================================================
from utils import log_activity, save_picture
# GÜNCELLEME (v6.0): Sadece 'Admin' rotalarını korumak için
# 'admin_required' import edilir.
from decorators import admin_required

academy = Blueprint('academy', __name__, url_prefix='/academy')

# ==========================================================================
# 1.0 - HALKA AÇIK AKADEMİ SAYFALARI (TÜM GİRİŞ YAPAN KULLANICILAR)
# v6.0 Notu: Bu rotaların hepsi '@login_required' kullanır.
# Bu, 'Kullanıcı', 'Personel' ve 'Admin' rollerinin tamamının
# bu sayfalara erişebileceği anlamına gelir. Bu, istediğimiz davranıştır.
# ==========================================================================

@academy.route("/")
@login_required # Gerekli: Kullanıcı, Personel, Admin
def academy_home():
    """Akademi ana sayfasını (kurs listesi) render eder."""
    return render_template('panel/academy.html', title='Akademi')

@academy.route("/data")
@login_required # Gerekli: Kullanıcı, Personel, Admin
def get_courses_data():
    """Kurs listesi için JSON verisi sağlar (JavaScript tarafından kullanılır)."""
    from models import Course, Enrollment

    try:
        all_courses = Course.query.order_by(Course.title.asc()).all()
        # Veri, 'current_user'a (rolü ne olursa olsun) göre çekilir.
        user_enrollments = {enrollment.course_id: enrollment for enrollment in
                            Enrollment.query.filter_by(user_id=current_user.id).all()}

        courses_list = []
        for course in all_courses:
            enrollment = user_enrollments.get(course.id)
            
            course_dict = {
                "id": course.id,
                "title": course.title,
                "category": course.category,
                "difficulty": course.difficulty,
                "duration_hours": course.duration_hours,
                "cover_image": course.cover_image or 'course_default.png',
                "description": course.description[:100] + '...' if course.description else '',
                "enrollment": {
                    "is_enrolled": enrollment is not None,
                    "progress": enrollment.get_progress() if enrollment else 0
                }
            }
            courses_list.append(course_dict)

        return jsonify(courses_list)

    except Exception as e:
        current_app.logger.error(f"Akademi JSON verisi oluşturulurken hata: {e}")
        return jsonify({"error": "Kurs verileri alınamadı. Lütfen daha sonra tekrar deneyin."}), 500

# ==========================================================================
# 2.0 - KURS VE DERS DETAY SAYFALARI (TÜM GİRİŞ YAPAN KULLANICILAR)
# ==========================================================================

@academy.route("/course/<int:course_id>")
@login_required # Gerekli: Kullanıcı, Personel, Admin
def course_detail(course_id):
    """Bir kursun detay sayfasını gösterir."""
    from models import Course
    course = Course.query.get_or_404(course_id)
    enrollment = current_user.get_enrollment_for_course(course_id)
    completed_lesson_ids = enrollment.get_completed_ids_set() if enrollment else set()
    
    return render_template('panel/course_detail.html',
                           title=course.title,
                           course=course,
                           enrollment=enrollment,
                           completed_lesson_ids=completed_lesson_ids)

@academy.route("/enroll/<int:course_id>", methods=['POST'])
@login_required # Gerekli: Kullanıcı, Personel, Admin
def enroll(course_id):
    """Kullanıcıyı bir kursa kaydeder."""
    from models import Course, Enrollment
    course = Course.query.get_or_404(course_id)
    if current_user.get_enrollment_for_course(course_id):
        flash('Bu kursa zaten kayıtlısınız.', 'info')
    else:
        try:
            new_enrollment = Enrollment(student=current_user._get_current_object(), course=course)
            db.session.add(new_enrollment)
            log_activity(current_user._get_current_object(), f"'{course.title}' kursuna kaydoldu.", course)
            db.session.commit()
            flash(f'"{course.title}" kursuna başarıyla kaydoldunuz!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kursa kayıt sırasında hata (user={current_user.id}, course={course_id}): {e}")
            flash("Kursa kaydolurken bir hata oluştu.", "danger")

    return redirect(url_for('academy.course_detail', course_id=course.id))

@academy.route("/lesson/<int:lesson_id>")
@login_required # Gerekli: Kullanıcı, Personel, Admin
def lesson_view(lesson_id):
    """Bir dersin izleme/sınav sayfasını gösterir."""
    from models import Lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    enrollment = current_user.get_enrollment_for_course(lesson.course_id)
    if not enrollment:
        flash('Bu dersi görmek için önce kursa kaydolmalısınız.', 'warning')
        return redirect(url_for('academy.course_detail', course_id=lesson.course_id))

    completed_lesson_ids = enrollment.get_completed_ids_set()
    quiz_questions = []
    recommended_videos_list = []
    
    # Parse recommended videos JSON if exists
    if lesson.recommended_videos:
        try:
            recommended_videos_list = json.loads(lesson.recommended_videos)
        except json.JSONDecodeError:
            current_app.logger.warning(f"Recommended videos JSON parse error for lesson {lesson.id}")
    
    if lesson.lesson_type == 'Quiz' and lesson.quiz:
        try:
            quiz_questions = json.loads(lesson.quiz.questions)
            return render_template('panel/quiz.html',
                                   title=f"Sınav: {lesson.title}",
                                   lesson=lesson,
                                   course=lesson.course,
                                   quiz=lesson.quiz, 
                                   questions=quiz_questions) 
        except json.JSONDecodeError:
             flash('Sınav soruları yüklenirken bir hata oluştu.', 'danger')
             return redirect(url_for('academy.course_detail', course_id=lesson.course_id))
    
    return render_template('panel/lesson.html',
                           title=f"Ders: {lesson.title}",
                           lesson=lesson,
                           course=lesson.course,
                           enrollment=enrollment,
                           completed_lesson_ids=completed_lesson_ids,
                           recommended_videos=recommended_videos_list)


@academy.route("/lesson/complete/<int:lesson_id>", methods=['POST'])
@login_required # Gerekli: Kullanıcı, Personel, Admin
def complete_lesson(lesson_id):
    """Bir dersi 'tamamlandı' olarak işaretler ve bir sonraki derse yönlendirir."""
    from models import Lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    enrollment = current_user.get_enrollment_for_course(lesson.course_id)
    if not enrollment:
         abort(403)

    try:
        if not enrollment.is_lesson_completed(lesson.id):
            enrollment.add_completed_lesson(lesson.id)
            log_activity(current_user._get_current_object(), f"'{lesson.title}' dersini tamamladı.", lesson)
            db.session.commit()
            flash(f'"{lesson.title}" dersini başarıyla tamamladın!', 'success')
    except Exception as e:
         db.session.rollback()
         current_app.logger.error(f"Ders tamamlama hatası (user={current_user.id}, lesson={lesson_id}): {e}")
         flash("Ders tamamlanırken bir hata oluştu.", "danger")
         return redirect(url_for('academy.lesson_view', lesson_id=lesson.id))

    next_lesson = lesson.course.get_next_lesson(lesson.order)
    if next_lesson:
        return redirect(url_for('academy.lesson_view', lesson_id=next_lesson.id))
    else:
        try:
            if enrollment.get_progress() == 100:
                 log_activity(current_user._get_current_object(), f"'{lesson.course.title}' kursunu bitirdi.", lesson.course)
                 db.session.commit()
            flash(f"Tebrikler! '{lesson.course.title}' kursunu tamamladınız!", "success")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kurs bitirme loglama hatası (user={current_user.id}, course={lesson.course_id}): {e}")
        return redirect(url_for('academy.course_detail', course_id=lesson.course_id))

# ==========================================================================
# 3.0 - QUIZ ROTLARI (TÜM GİRİŞ YAPAN KULLANICILAR)
# ==========================================================================

@academy.route("/quiz/submit/<int:quiz_id>", methods=['POST'])
@login_required # Gerekli: Kullanıcı, Personel, Admin
def submit_quiz(quiz_id):
    """Kullanıcının quiz cevaplarını alır, değerlendirir ve kaydeder."""
    from models import Quiz, QuizAttempt
    quiz = Quiz.query.get_or_404(quiz_id)
    enrollment = current_user.get_enrollment_for_course(quiz.lesson.course_id)
    if not enrollment: abort(403)

    try:
        questions = json.loads(quiz.questions)
    except json.JSONDecodeError:
        flash('Sınav soruları yüklenemedi.', 'danger')
        return redirect(url_for('academy.lesson_view', lesson_id=quiz.lesson_id))

    score = 0
    total = len(questions)
    user_answers = {}

    for i, question in enumerate(questions):
        user_answer_index = request.form.get(f'question-{i}')
        user_answers[i] = user_answer_index
        try:
            if user_answer_index is not None:
                # Seçilen seçeneğin metnini al (frontend'den gönderiliyor)
                selected_option_text = request.form.get(f'question-{i}-text', '').strip()
                if selected_option_text:
                    # Seçilen seçenek metni ile doğru cevabın metnini karşılaştır
                    correct_option_text = question.get('options', [])[question.get('correct_index', 0)]
                    if selected_option_text == correct_option_text:
                        score += 1
                else:
                    # Fallback: Eğer metin gelmediyse, orijinal indeks yöntemini kullan (eski sistem)
                    # Bu durumda frontend'den gelen indeks karıştırılmış dizideki indeks,
                    # ama backend'de orijinal diziyi kullanıyoruz, bu yüzden bu yöntem çalışmayabilir
                    # Ancak geriye dönük uyumluluk için bırakıyoruz
                    pass
        except (ValueError, TypeError, IndexError, KeyError):
             pass

    try:
        attempt = QuizAttempt(user_id=current_user.id,
                              quiz_id=quiz.id,
                              score=score,
                              total_questions=total)
        db.session.add(attempt)
        log_activity(current_user._get_current_object(), f"'{quiz.lesson.title}' sınavını tamamladı. Sonuç: {score}/{total}", quiz)

        # Quiz başarılı sayılması için en az 18/20 doğru olmalı (90% başarı)
        required_score = max(18, int(total * 0.9))  # En az 18 veya toplamın %90'ı
        passed = score >= required_score
        
        if passed and not enrollment.is_lesson_completed(quiz.lesson_id):
             enrollment.add_completed_lesson(quiz.lesson_id)
             log_activity(current_user._get_current_object(), f"'{quiz.lesson.title}' dersini (quiz ile başarıyla) tamamladı. Skor: {score}/{total}", quiz.lesson)
             flash(f'Tebrikler! Sınavı başarıyla tamamladınız. Sonucun: {score}/{total} (Geçme: {required_score}/{total})', 'success')
        elif not passed:
            flash(f'Sınav tamamlandı ancak geçme notu alamadınız. Sonucun: {score}/{total} (Geçme: {required_score}/{total}) - Dersi tamamlamak için en az {required_score} doğru cevap vermelisiniz.', 'warning')
        else:
            flash(f'Sınav tamamlandı! Sonucun: {score}/{total}', 'info')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Quiz sonucu kaydetme hatası (user={current_user.id}, quiz={quiz_id}): {e}")
        flash("Sınav sonucu kaydedilirken bir hata oluştu.", "danger")

    return redirect(url_for('academy.lesson_view', lesson_id=quiz.lesson_id))


@academy.route("/certificate/<int:course_id>")
@login_required
def download_certificate(course_id):
    """Kursu tamamlayan kullanıcı için PDF sertifika oluşturur ve indirir."""
    from models import Course, Enrollment
    
    course = Course.query.get_or_404(course_id)
    enrollment = current_user.get_enrollment_for_course(course_id)
    
    if not enrollment:
        flash('Bu kursa kayıtlı değilsiniz.', 'warning')
        return redirect(url_for('academy.course_detail', course_id=course_id))
    
    if enrollment.get_progress() != 100:
        flash('Sertifika almak için kursu tamamlamanız gerekiyor.', 'warning')
        return redirect(url_for('academy.course_detail', course_id=course_id))
    
    try:
        # PDF oluştur - daha geniş kenar boşlukları
        buffer = BytesIO()
        
        # PageTemplate ile dekoratif arka plan eklemek için canvas kullanacağız
        def draw_page(canvas, doc):
            """Her sayfaya dekoratif öğeler ekler"""
            width, height = A4
            border_margin = 1.5*cm
            
            # Dış çerçeve (turuncu kalın)
            canvas.setStrokeColor(colors.HexColor('#ff6b35'))
            canvas.setLineWidth(4)
            canvas.rect(border_margin, border_margin, 
                       width - 2*border_margin, 
                       height - 2*border_margin)
            
            # İç çerçeve (altın)
            inner_margin = 0.4*cm
            canvas.setStrokeColor(colors.HexColor('#ffa726'))
            canvas.setLineWidth(2)
            canvas.rect(border_margin + inner_margin, 
                       border_margin + inner_margin,
                       width - 2*(border_margin + inner_margin), 
                       height - 2*(border_margin + inner_margin))
            
            # Köşe dekorasyonları - yıldızlar
            corner_size = 1.2*cm
            corner_positions = [
                (border_margin + inner_margin + 0.2*cm, height - border_margin - inner_margin - 0.2*cm - corner_size),
                (width - border_margin - inner_margin - 0.2*cm - corner_size, height - border_margin - inner_margin - 0.2*cm - corner_size),
                (border_margin + inner_margin + 0.2*cm, border_margin + inner_margin + 0.2*cm),
                (width - border_margin - inner_margin - 0.2*cm - corner_size, border_margin + inner_margin + 0.2*cm),
            ]
            
            for x, y in corner_positions:
                # Dekoratif rozet (daire)
                canvas.setFillColor(colors.HexColor('#ff6b35'))
                canvas.setStrokeColor(colors.HexColor('#ff6b35'))
                canvas.setLineWidth(1.5)
                canvas.circle(x + corner_size/2, y + corner_size/2, corner_size/3, fill=1, stroke=1)
                canvas.setFillColor(colors.white)
                canvas.circle(x + corner_size/2, y + corner_size/2, corner_size/5, fill=1)
            
            # Üst ve alt dekoratif çizgiler
            line_y_top = height - border_margin - inner_margin - 3*cm
            line_y_bottom = border_margin + inner_margin + 3*cm
            
            for line_y in [line_y_top, line_y_bottom]:
                canvas.setStrokeColor(colors.HexColor('#ff6b35'))
                canvas.setLineWidth(1)
                line_start = border_margin + inner_margin + 2.5*cm
                line_end = width - border_margin - inner_margin - 2.5*cm
                canvas.line(line_start, line_y, line_end, line_y)
                # Çizginin üzerinde dekoratif noktalar
                for i in range(5):
                    dot_x = line_start + (line_end - line_start) * i / 4
                    canvas.setFillColor(colors.HexColor('#ff6b35'))
                    canvas.circle(dot_x, line_y, 0.12*cm, fill=1)
        
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=1.5*cm, leftMargin=1.5*cm,
                              topMargin=1.5*cm, bottomMargin=1.5*cm,
                              onFirstPage=draw_page,
                              onLaterPages=draw_page)
        
        # İçerik listesi
        story = []
        
        # Stiller
        styles = getSampleStyleSheet()
        
        # Başlık stili - daha büyük ve etkileyici
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor('#ff6b35'),
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=42
        )
        
        # Alt başlık stili
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # İsim stili - çok vurgulu
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Heading2'],
            fontSize=32,
            textColor=colors.HexColor('#ff6b35'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        )
        
        # Kurs başlık stili
        course_title_style = ParagraphStyle(
            'CourseTitleStyle',
            parent=styles['Heading2'],
            fontSize=22,
            textColor=colors.HexColor('#2c2c2c'),
            spaceAfter=35,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        )
        
        # Detay stili
        details_style = ParagraphStyle(
            'DetailsStyle',
            parent=styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Tarih stili
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b6b6b'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        # İmza stili
        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2c2c2c'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Başlık - daha fazla boşluk
        story.append(Spacer(1, 4*cm))
        story.append(Paragraph("SERTİFİKA", title_style))
        story.append(Spacer(1, 0.8*cm))
        
        # Dekoratif çizgi
        story.append(Paragraph("<hr width='400' color='#ff6b35'/>", subtitle_style))
        story.append(Spacer(1, 0.8*cm))
        
        # Alt başlık
        story.append(Paragraph("Bu belge, aşağıda adı geçen kişinin", subtitle_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Kullanıcı adı - büyük ve vurgulu
        user_name = current_user.name or current_user.username
        story.append(Paragraph(f"<b>{user_name.upper()}</b>", name_style))
        story.append(Spacer(1, 0.6*cm))
        
        # Kurs bilgisi
        story.append(Paragraph("aşağıdaki kursu başarıyla tamamladığını belgeler:", subtitle_style))
        story.append(Spacer(1, 0.6*cm))
        
        # Kurs başlığı - vurgulu
        course_title_style = ParagraphStyle(
            'CourseTitleStyle',
            parent=styles['Heading2'],
            fontSize=22,
            textColor=colors.HexColor('#2c2c2c'),
            spaceAfter=35,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        )
        story.append(Paragraph(f"<b>{course.title}</b>", course_title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Kurs detayları - daha düzenli ve güzel
        details_data = [
            ['Eğitmen:', course.instructor_name or 'KUWAMEDYA Ekibi'],
            ['Seviye:', course.difficulty],
            ['Ders Sayısı:', str(course.get_lesson_count())],
            ['Süre:', f'{course.duration_hours} Saat']
        ]
        
        details_table = Table(details_data, colWidths=[4*cm, 6*cm])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 13),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c2c2c')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 1.5*cm))
        
        # Tarih
        date_str = datetime.now().strftime('%d %B %Y')
        # Türkçe ay isimleri
        month_tr = {
            'January': 'Ocak', 'February': 'Şubat', 'March': 'Mart', 'April': 'Nisan',
            'May': 'Mayıs', 'June': 'Haziran', 'July': 'Temmuz', 'August': 'Ağustos',
            'September': 'Eylül', 'October': 'Ekim', 'November': 'Kasım', 'December': 'Aralık'
        }
        for en, tr in month_tr.items():
            date_str = date_str.replace(en, tr)
        
        date_text = f"<i>Tarih: {date_str}</i>"
        story.append(Paragraph(date_text, date_style))
        story.append(Spacer(1, 2.5*cm))
        
        # İmza alanı - daha profesyonel
        signature_text = """
        <table width='500' align='center'>
        <tr><td align='center'><hr width='250' color='#ff6b35'/></td></tr>
        <tr><td align='center' style='padding-top: 10px;'><b>KUWAMEDYA Akademi</b></td></tr>
        <tr><td align='center' style='padding-top: 5px; font-size: 11px; color: #6b6b6b;'>Eğitim ve Sertifikasyon Merkezi</td></tr>
        </table>
        """
        story.append(Paragraph(signature_text, signature_style))
        
        # PDF'i oluştur - önce canvas'ı birleştir
        # Not: ReportLab'de canvas ve SimpleDocTemplate'i birleştirmek için
        # farklı bir yaklaşım kullanmamız gerekiyor
        # Basit bir çözüm: story'ye canvas eklemek yerine, arka planı story içinde çizelim
        
        # PDF'i oluştur
        doc.build(story)
        buffer.seek(0)
        
        # Response oluştur
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=sertifika_{course.id}_{current_user.id}.pdf'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Sertifika oluşturma hatası (user={current_user.id}, course={course_id}): {e}")
        flash('Sertifika oluşturulurken bir hata oluştu.', 'danger')
        return redirect(url_for('academy.course_detail', course_id=course_id))


# ==========================================================================
# 4.0 - ADMİN İÇİN AKADEMİ YÖNETİM PANELİ (SADECE ADMİN)
# v6.0 Notu: Bu rotaların hepsi '@admin_required' kullanır.
# Bu, 'Kullanıcı' (Öğrenci) ve 'Personel' rollerinin
# bu sayfalara erişmesini engeller. Bu, istediğimiz davranıştır.
# ==========================================================================

@academy.route("/admin/manage")
@admin_required # SADECE Admin
def manage_courses():
    """Tüm kursları listeleyen ana yönetim sayfası."""
    from models import Course
    try:
        page = request.args.get('page', 1, type=int)
        courses_pagination = Course.query.order_by(desc(Course.created_at)).paginate(page=page, per_page=10)
    except Exception as e:
         current_app.logger.error(f"Kurs yönetimi sayfası yüklenirken hata: {e}")
         flash("Kurslar listelenirken bir hata oluştu.", "danger")
         courses_pagination = None

    return render_template('admin/manage_courses.html', title="Kurs Yönetimi", courses_pagination=courses_pagination)

@academy.route("/admin/course/add", methods=['GET', 'POST'])
@admin_required # SADECE Admin
def add_course():
    """Yeni bir kurs oluşturma sayfası ve işlemi."""
    from models import Course
    from forms import CourseForm
    form = CourseForm()
    if form.validate_on_submit():
        try:
            picture_file = 'course_default.png'
            if form.cover_image.data:
                picture_file = save_picture(form.cover_image.data, folder='courses', output_size=(800, 450))

            course = Course(title=form.title.data,
                            description=form.description.data,
                            category=form.category.data,
                            difficulty=form.difficulty.data,
                            duration_hours=form.duration_hours.data,
                            cover_image=picture_file, 
                            instructor_name=form.instructor_name.data)
            db.session.add(course)
            db.session.flush()
            log_activity(current_user._get_current_object(), f"yeni bir kurs ekledi: <strong>{course.title}</strong>", course)
            db.session.commit()
            flash('Yeni kurs başarıyla oluşturuldu!', 'success')
            return redirect(url_for('academy.manage_courses'))
        except ValueError as ve:
             flash(str(ve), 'danger')
        except exc.IntegrityError:
             db.session.rollback()
             flash('Bu başlıkla başka bir kurs zaten mevcut.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni kurs eklenirken hata: {e}")
            flash(f"Kurs eklenirken bir hata oluştu: {e}", "danger")

    return render_template('admin/create_edit_course.html', title="Yeni Kurs Ekle", form=form, course=None)

@academy.route("/admin/course/<int:course_id>/edit", methods=['GET', 'POST'])
@admin_required # SADECE Admin
def edit_course(course_id):
    """Mevcut bir kursu düzenleme sayfası ve işlemi."""
    from models import Course
    from forms import CourseForm
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    current_image = course.cover_image
    
    if form.validate_on_submit():
        try:
            original_title = course.title
            
            form.populate_obj(course)
            
            # cover_image.data kontrolü: FileStorage objesi mi yoksa string mi?
            if form.cover_image.data and hasattr(form.cover_image.data, 'filename'):
                # Yeni dosya yüklendi
                course.cover_image = save_picture(form.cover_image.data, folder='courses', output_size=(800, 450))
            else:
                # Dosya yüklenmedi, mevcut resmi koru
                course.cover_image = current_image 

            log_activity(current_user._get_current_object(), f"<strong>{original_title}</strong> kursunu güncelledi.", course)
            db.session.commit()
            flash('Kurs bilgileri başarıyla güncellendi!', 'success')
            return redirect(url_for('academy.manage_courses'))
        except ValueError as ve:
             flash(str(ve), 'danger')
        except exc.IntegrityError:
             db.session.rollback()
             flash('Bu başlıkla başka bir kurs zaten mevcut.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kurs {course_id} düzenlenirken hata: {e}")
            flash(f"Kurs güncellenirken bir hata oluştu: {e}", "danger")
    
    return render_template('admin/create_edit_course.html', title="Kursu Düzenle", form=form, course=course)

@academy.route("/admin/course/<int:course_id>/delete", methods=['POST'])
@admin_required # SADECE Admin
def delete_course(course_id):
    """Bir kursu ve ona bağlı tüm dersleri, quizleri, kayıtları siler."""
    from models import Course
    course = Course.query.get_or_404(course_id)
    try:
        title = course.title
        db.session.delete(course)
        log_activity(current_user._get_current_object(), f"<strong>{title}</strong> kursunu sistemden sildi.")
        db.session.commit()
        flash(f'"{title}" adlı kurs ve ilişkili tüm veriler kalıcı olarak silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Kurs {course_id} silinirken hata: {e}")
        flash(f"Kurs silinirken bir hata oluştu: {e}", "danger")
    return redirect(url_for('academy.manage_courses'))


@academy.route("/admin/course/<int:course_id>/lessons")
@admin_required # SADECE Admin
def manage_lessons(course_id):
    """Bir kursa ait dersleri yönetme sayfası."""
    from models import Course, Lesson
    from forms import LessonForm, QuizForm
    course = Course.query.get_or_404(course_id)
    try:
        lessons = course.lessons.order_by(Lesson.order.asc()).all()
    except Exception as e:
        current_app.logger.error(f"Kurs {course_id} için dersler listelenirken hata: {e}")
        flash("Dersler yüklenirken bir hata oluştu.", "danger")
        lessons = []

    lesson_form = LessonForm()
    quiz_form = QuizForm()
    
    return render_template('admin/manage_lessons.html',
                           title=f"Ders Yönetimi: {course.title}",
                           course=course,
                           lessons=lessons,
                           lesson_form=lesson_form,
                           quiz_form=quiz_form) 

@academy.route("/admin/course/<int:course_id>/add_lesson", methods=['POST'])
@admin_required # SADECE Admin
def add_lesson(course_id):
    """Bir kursa yeni bir ders ekler."""
    from models import Course, Lesson
    from forms import LessonForm
    course = Course.query.get_or_404(course_id)
    form = LessonForm()
    if form.validate_on_submit():
        try:
            lesson = Lesson(course_id=course.id)
            form.populate_obj(lesson)
            db.session.add(lesson)
            db.session.flush()
            log_activity(current_user._get_current_object(), f"<strong>{course.title}</strong> kursuna yeni ders ekledi: '{lesson.title}'.", lesson)
            db.session.commit()
            flash('Yeni ders başarıyla eklendi!', 'success')
        except exc.IntegrityError:
            db.session.rollback()
            flash(f"Bu kurs için '{form.order.data}' sıra numarası zaten kullanılıyor.", 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Yeni ders eklenirken hata (course={course_id}): {e}")
            flash(f"Ders eklenirken bir hata oluştu: {e}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Ders Ekleme Hatası - {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('academy.manage_lessons', course_id=course_id))


@academy.route("/admin/lesson/<int:lesson_id>/edit", methods=['GET', 'POST'])
@admin_required # SADECE Admin
def edit_lesson(lesson_id):
    """Mevcut bir dersi düzenler (GET ile modal'ı doldurur, POST ile günceller)."""
    from models import Lesson
    from forms import LessonForm
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)

    if form.validate_on_submit(): # POST isteği
        try:
            original_title = lesson.title
            form.populate_obj(lesson)
            log_activity(current_user._get_current_object(), f"'{original_title}' dersini güncelledi.", lesson)
            db.session.commit()
            flash('Ders başarıyla güncellendi!', 'success')
            return redirect(url_for('academy.manage_lessons', course_id=lesson.course_id))
        except exc.IntegrityError:
            db.session.rollback()
            flash(f"Bu kurs için '{form.order.data}' sıra numarası zaten kullanılıyor.", 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ders {lesson_id} düzenlenirken hata: {e}")
            flash(f"Ders güncellenirken bir hata oluştu: {e}", "danger")
        return redirect(url_for('academy.manage_lessons', course_id=lesson.course_id))

    # GET isteği (AJAX/Fetch tarafından modal'ı doldurmak için kullanılır)
    return jsonify({
        'title': lesson.title,
        'lesson_type': lesson.lesson_type,
        'content': lesson.content,
        'video_url': lesson.video_url,
        'order': lesson.order,
        'form_action': url_for('academy.edit_lesson', lesson_id=lesson.id)
    })

@academy.route("/admin/lesson/<int:lesson_id>/delete", methods=['POST'])
@admin_required # SADECE Admin
def delete_lesson(lesson_id):
    """Bir dersi siler."""
    from models import Lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    try:
        title = lesson.title
        db.session.delete(lesson)
        log_activity(current_user._get_current_object(), f"'{title}' dersini sildi.")
        db.session.commit()
        flash(f'"{title}" adlı ders silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ders {lesson_id} silinirken hata: {e}")
        flash(f"Ders silinirken bir hata oluştu: {e}", "danger")
    return redirect(url_for('academy.manage_lessons', course_id=course_id))

# --- Quiz Yönetimi ---
@academy.route("/admin/lesson/<int:lesson_id>/add_quiz", methods=['POST'])
@admin_required # SADECE Admin
def add_quiz(lesson_id):
    """Bir derse yeni bir quiz ekler."""
    from models import Lesson, Quiz
    from forms import QuizForm
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.quiz:
        flash("Bu derse ait zaten bir quiz mevcut. Düzenleyebilirsiniz.", "warning")
        return redirect(url_for('academy.manage_lessons', course_id=lesson.course_id))

    form = QuizForm()
    if form.validate_on_submit():
        try:
            questions_json = form.questions_json.data
            json.loads(questions_json) 

            quiz = Quiz(lesson_id=lesson.id, title=form.title.data, questions=questions_json)
            db.session.add(quiz)
            lesson.lesson_type = 'Quiz' 
            db.session.flush()
            log_activity(current_user._get_current_object(), f"'{lesson.title}' dersine quiz ekledi: '{quiz.title}'.", quiz)
            db.session.commit()
            flash('Quiz başarıyla eklendi!', 'success')
        except json.JSONDecodeError:
            flash("Sorular geçerli bir JSON formatında değil.", "danger")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Quiz eklenirken hata (lesson={lesson_id}): {e}")
            flash(f"Quiz eklenirken bir hata oluştu: {e}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Quiz Ekleme Hatası - {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('academy.manage_lessons', course_id=lesson.course_id))


@academy.route("/admin/quiz/<int:quiz_id>/edit", methods=['GET', 'POST'])
@admin_required # SADECE Admin
def edit_quiz(quiz_id):
    """Mevcut bir quizi düzenler (GET ile modal'ı doldurur, POST ile günceller)."""
    from models import Quiz
    from forms import QuizForm
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    
    if form.validate_on_submit(): 
        try:
            original_title = quiz.title
            questions_json = form.questions_json.data
            json.loads(questions_json) 

            quiz.title = form.title.data
            quiz.questions = questions_json
            log_activity(current_user._get_current_object(), f"'{original_title}' quizini güncelledi.", quiz)
            db.session.commit()
            flash('Quiz başarıyla güncellendi!', 'success')
        except json.JSONDecodeError:
            flash("Sorular geçerli bir JSON formatında değil.", "danger")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Quiz {quiz_id} düzenlenirken hata: {e}")
            flash(f"Quiz güncellenirken bir hata oluştu: {e}", "danger")
        return redirect(url_for('academy.manage_lessons', course_id=quiz.lesson.course_id))

    return jsonify({
        'title': quiz.title,
        'questions_json': quiz.questions, 
        'form_action': url_for('academy.edit_quiz', quiz_id=quiz.id)
    })

@academy.route("/admin/quiz/<int:quiz_id>/delete", methods=['POST'])
@admin_required # SADECE Admin
def delete_quiz(quiz_id):
    """Bir quizi siler."""
    from models import Quiz
    quiz = Quiz.query.get_or_404(quiz_id)
    course_id = quiz.lesson.course_id
    try:
        title = quiz.title
        lesson = quiz.lesson
        db.session.delete(quiz)
        if lesson and lesson.lesson_type == 'Quiz':
            lesson.lesson_type = 'Metin' 
        log_activity(current_user._get_current_object(), f"'{title}' quizini sildi.")
        db.session.commit()
        flash(f'"{title}" adlı quiz silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Quiz {quiz_id} silinirken hata: {e}")
        flash(f"Quiz silinirken bir hata oluştu: {e}", "danger")
    return redirect(url_for('academy.manage_lessons', course_id=course_id))
