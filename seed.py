import random
import json
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import exc # Hata yakalama için

# Eklentiler ve Modeller (fonksiyon içinde import edilecek)
from extensions import db, bcrypt
# from models import (User, Project, Technology, Package, Testimonial, Sale,
#                     Commission, Course, Lesson, Enrollment, Quiz, QuizAttempt, ActivityLog)
# Prim Hesaplama Motoru (fonksiyon içinde import edilecek)
# from commission_engine import calculate_and_record_commission

# ==========================================================================
# Geliştirilmiş Veritabanı Tohumlama (seed.py) - v2.0 Bumblebee Edition
#
# YENİLİKLER:
# 1. MODEL UYUMLULUĞU: `models.py`'deki tüm değişikliklerle uyumlu hale getirildi:
#    - `User` oluşturulurken `google_id` alanı bazı kullanıcılar için eklendi.
#    - Normal kullanıcılar için şifre (`password='password123'`) verilirken,
#      Google ile oluşturulanlar için şifre verilmiyor (`models.py`'deki kontrol bunu halleder).
#    - `User.image_file` artık atanmıyor, `avatar()` metodu kullanılacak (Gravatar/default).
#    - Diğer modellere eklenen `created_at`/`updated_at` gibi alanlar otomatik dolacak.
#    - İlişkiler (`backref` ve `cascade`) güncel modellere göre çalışacak.
#
# 2. DAHA GERÇEKÇİ VERİ:
#    - Faker kullanılarak daha çeşitli ve anlamlı veriler (proje açıklamaları,
#      kurs içerikleri, kullanıcı biyografileri vb.) üretildi.
#    - Aktivite logları daha çeşitli senaryoları yansıtacak şekilde güncellendi.
#
# 3. SAĞLAM HATA YÖNETİMİ: Veritabanı işlemleri sırasında oluşabilecek
#    hataları (`IntegrityError` vb.) yakalamak ve loglamak için `try...except`
#    blokları iyileştirildi. Özellikle prim hesaplama gibi zincirleme
#    işlemlerde daha dikkatli davranıldı.
#
# 4. TEMİZ KOD YAPISI: Kod okunabilirliği artırıldı, adımlar daha net
#    olarak belirtildi, importlar fonksiyon içine taşındı.
# ==========================================================================

def seed_data():
    """
    Veritabanını sıfırlar ve kapsamlı test verileriyle doldurur.
    'flask seed' komutuyla çağrılır.
    """
    # Gerekli modülleri burada import et
    from models import (User, Project, Technology, Package, Testimonial, Sale,
                        Commission, Course, Lesson, Enrollment, Quiz, QuizAttempt, ActivityLog)
    from commission_engine import calculate_and_record_commission
    from flask import current_app # Loglama için

    try:
        current_app.logger.info("--- Veritabanı Tohumlama İşlemi Başlatıldı ---")

        current_app.logger.info("1/9: Mevcut veritabanı temizleniyor ve tablolar yeniden oluşturuluyor...")
        # db.session.remove() # Önceki session'ı kapat (nadiren gerekir)
        db.drop_all()
        db.create_all()

        fake = Faker('tr_TR') # Türkçe veri üretimi için

        current_app.logger.info("2/9: Kullanıcılar (Admin, Personel, Google) oluşturuluyor...")
        # Şifreleri bcrypt ile hash'leyerek oluşturmak yerine User modelindeki __init__ veya set_password kullanılıyor.
        # GÜVENLİK: Admin şifresi güvenli bir değerle değiştirildi
        # Admin Giriş Bilgileri:
        # - Kullanıcı Adı: admin
        # - E-posta: admin@kuwamedya.com
        # - Şifre: Kuwamedya2025!Admin
        admin_user = User(
            name='Bülent Bey', username='admin', email='admin@kuwamedya.com',
            password='Kuwamedya2025!Admin', role='Admin', title='Kurucu & CEO',
            bio=fake.paragraph(nb_sentences=5), is_active=True
        )
        db.session.add(admin_user)

        # Örnek ekip üyeleri (minimum 3 kişi - iletişim için)
        personnel_list = []
        
        # Varsayılan personel (Yusuf Duhan ve Yiğit Haktan)
        default_personnel = [
            {
                'name': 'Yusuf Duhan',
                'username': 'yusufduhan',
                'email': 'yusuf.duhan@kuwamedya.com',
                'password': 'DefaultPass123!',
                'role': 'Personel',
                'title': 'Web Yazılımcı',
                'bio': 'Web geliştirme konusunda uzman, modern teknolojilerle çözümler üretiyor.',
                'quote': 'Teknoloji ile hayalleri gerçeğe dönüştürüyoruz.',
                'is_active': True
            },
            {
                'name': 'Yiğit Haktan',
                'username': 'yigithaktan',
                'email': 'yigit.haktan@kuwamedya.com',
                'password': 'DefaultPass123!',
                'role': 'Personel',
                'title': 'Dijital Pazarlama',
                'bio': 'Dijital pazarlama stratejileri ve sosyal medya yönetimi konusunda deneyimli.',
                'quote': 'Markanızı dijital dünyada öne çıkarıyoruz.',
                'is_active': True
            }
        ]
        
        for person_data in default_personnel:
            person = User(**person_data)
            personnel_list.append(person)
            db.session.add(person)
        
        # Sadece Ayşe Yılmaz'ı ekle (Mehmet Demir ve Zeynep Kaya kaldırıldı)
        user = User(
            name='Ayşe Yılmaz',
            username=fake.user_name() + '0',
            email='ekip1@kuwamedya.com',
            password='password123',
            role='Personel',
            title='Dijital Pazarlama Uzmanı',
            quote='Dijital dünyada markanızı öne çıkarıyoruz.',
            bio=fake.paragraph(nb_sentences=3),
            is_active=True
        )
        personnel_list.append(user)
        db.session.add(user)

        # İlk commit kullanıcıları veritabanına yazmak için
        try:
            db.session.commit()
            current_app.logger.info("Kullanıcılar başarıyla eklendi.")
        except exc.IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Kullanıcı eklenirken IntegrityError: {e}")
            # Bu kritik bir hata, devam etmeyebiliriz.
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kullanıcı eklenirken genel hata: {e}")
            raise


        current_app.logger.info("3/9: Teknolojiler oluşturuluyor...")
        tech_names = ['Python', 'Flask', 'JavaScript', 'SQLAlchemy', 'React', 'Vue.js', 'PostgreSQL', 'Docker', 'AWS', 'Bootstrap 5', 'CSS3', 'HTML5']
        tech_objects = {name: Technology(name=name) for name in tech_names}
        db.session.add_all(tech_objects.values())
        db.session.commit()
        current_app.logger.info("Teknolojiler başarıyla eklendi.")


        current_app.logger.info("4/9: Portfolyo projeleri oluşturuluyor...")
        projects_list = []
        # Her kategoriden 1 örnek proje ekle
        project_categories = [
            {
                'category': 'Web Yazılım',
                'title': 'Modern Kurumsal Web Sitesi',
                'description': 'Modern ve kullanıcı dostu arayüz tasarımı ile kurumsal web sitesi geliştirme projesi. Responsive tasarım ve SEO optimizasyonu ile tamamlandı.',
                'image_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop'
            },
            {
                'category': 'Dijital Pazarlama',
                'title': 'SEO ve İçerik Pazarlama Stratejisi',
                'description': 'Kapsamlı SEO optimizasyonu ve içerik pazarlama stratejisi ile marka görünürlüğünü artıran dijital pazarlama projesi.',
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop'
            },
            {
                'category': 'Marka Kimliği',
                'title': 'Kurumsal Marka Kimliği Tasarımı',
                'description': 'Logo tasarımı, kurumsal renk paleti ve marka kimliği rehberi ile tutarlı bir marka imajı oluşturma projesi.',
                'image_url': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=600&fit=crop'
            },
            {
                'category': 'Mobil Uygulama',
                'title': 'İOS ve Android Mobil Uygulama',
                'description': 'Kullanıcı dostu arayüz ve performans odaklı geliştirme ile iOS ve Android platformları için native mobil uygulama projesi.',
                'image_url': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=600&fit=crop'
            }
        ]
        
        for proj_data in project_categories:
            project_techs = random.sample(list(tech_objects.values()), k=random.randint(2, 5))
            project = Project(
                title=proj_data['title'],
                category=proj_data['category'],
                client=fake.company(),
                project_date=fake.date_between(start_date='-2y', end_date='today'),
                description=proj_data['description'],
                cover_image_url=proj_data['image_url'],  # Lisanssız Unsplash resmi
                live_url=None,
                technologies=project_techs
            )
            db.session.add(project)
            projects_list.append(project)
        
        db.session.commit()
        current_app.logger.info("Projeler başarıyla eklendi.")


        current_app.logger.info("5/9: Müşteri yorumları ve hizmet paketleri oluşturuluyor...")
        # Türkçe müşteri yorumları
        turkish_testimonials = [
            {
                'author_name': 'Ahmet Yılmaz',
                'author_title': 'Genel Müdür @ Teknoloji A.Ş.',
                'quote': 'Kuwamedya ile çalışmaktan çok memnunuz. Profesyonel yaklaşımları ve hızlı çözüm üretme yetenekleri sayesinde dijital dönüşümümüzü başarıyla tamamladık.',
                'rating': 5,
                'is_featured': True
            },
            {
                'author_name': 'Ayşe Demir',
                'author_title': 'Pazarlama Müdürü @ Moda Markası',
                'quote': 'Sosyal medya yönetimimizi onlara bıraktıktan sonra takipçi sayımız ve etkileşim oranlarımız ciddi şekilde arttı. Teşekkürler!',
                'rating': 5,
                'is_featured': True
            },
            {
                'author_name': 'Mehmet Kaya',
                'author_title': 'Kurucu @ Startup Firması',
                'quote': 'Web sitemizin tasarımı ve işlevselliği harika. Müşteri memnuniyetimiz arttı, işimiz büyüdü. Kesinlikle tavsiye ederim.',
                'rating': 5,
                'is_featured': True
            },
            {
                'author_name': 'Zeynep Şahin',
                'author_title': 'İK Müdürü @ Şirket',
                'quote': 'Personel temin konusunda çok yardımcı oldular. İhtiyacımız olan kalifiye elemanları kısa sürede bulduk.',
                'rating': 4,
                'is_featured': False
            },
            {
                'author_name': 'Can Özkan',
                'author_title': 'CEO @ Dijital Ajans',
                'quote': 'SEO çalışmaları sayesinde organik trafiğimiz %300 arttı. Artık daha fazla müşteriye ulaşıyoruz.',
                'rating': 5,
                'is_featured': True
            },
            {
                'author_name': 'Elif Çelik',
                'author_title': 'Marka Müdürü @ Perakende',
                'quote': 'Dijital pazarlama stratejileri gerçekten işe yaradı. Satışlarımız önemli ölçüde yükseldi.',
                'rating': 5,
                'is_featured': False
            },
            {
                'author_name': 'Burak Yıldız',
                'author_title': 'Proje Yöneticisi @ İnşaat',
                'quote': 'Kurumsal kimlik çalışmaları ve web tasarımı konusunda çok başarılılar. Profesyonel ekiple çalışmak keyifli.',
                'rating': 5,
                'is_featured': True
            }
        ]
        for testimonial_data in turkish_testimonials:
            testimonial = Testimonial(**testimonial_data)
            db.session.add(testimonial)

        packages_data = [
            {'name': 'Temel SEO', 'order': 1, 'description': 'Yeni başlayanlar için temel SEO hizmetleri.', 'price_monthly': 1500, 'price_yearly': 15000, 'features': 'Anahtar Kelime Analizi\nTeknik SEO Denetimi\nAylık Raporlama', 'is_popular': False},
            {'name': 'Pro Sosyal Medya', 'order': 2, 'description': 'Markanızı sosyal medyada profesyonelce yönetin.', 'price_monthly': 2500, 'price_yearly': 25000, 'features': 'Haftalık 5 Gönderi\nReklam Yönetimi\nAylık Raporlama\nEtkileşim Analizi', 'is_popular': True},
            {'name': 'Kurumsal Web Paketi', 'order': 3, 'description': 'Modern ve hızlı kurumsal web sitesi.', 'price_monthly': 3000, 'price_yearly': 30000, 'features': 'Modern Tasarım\nAdmin Paneli\n1 Yıl Hosting\nSEO Uyumlu', 'is_popular': False},
             {'name': 'E-Ticaret Çözümü', 'order': 4, 'description': 'Anahtar teslim e-ticaret sitesi.', 'price_monthly': 4500, 'price_yearly': 45000, 'features': 'Özel Tasarım\nÖdeme Sistemi Entegrasyonu\nÜrün Yönetimi\nSEO Altyapısı', 'is_popular': False},
        ]
        packages_list = []
        for data in packages_data:
            package = Package(**data)
            packages_list.append(package)
            db.session.add(package)
        db.session.commit()
        current_app.logger.info("Yorumlar ve paketler başarıyla eklendi.")


        current_app.logger.info("6/9: Satışlar oluşturuluyor ve primler hesaplanıyor...")
        sales_list = []
        active_personnel = [p for p in personnel_list if p.is_active] # Sadece aktif personel satış yapabilir
        for person in active_personnel:
            for _ in range(random.randint(3, 12)): # Satış sayısı azaltıldı
                # Satışı oluşturmadan önce personelin ID'sinin olduğundan emin ol
                if person.id is None:
                    db.session.flush([person]) # ID ataması için flush et
                    if person.id is None: # Hala ID yoksa bu kullanıcıyı atla
                         current_app.logger.warning(f"Kullanıcı {person.username} için ID alınamadı, satış eklenemiyor.")
                         continue

                sold_package = random.choice(packages_list)
                sale = Sale(
                    product_name=sold_package.name,
                    amount=random.choice([sold_package.price_monthly, sold_package.price_yearly / 12]), # Rastgele aylık/yıllık eşdeğeri
                    author=person, # İlişkiyi kur
                    date_posted=fake.date_time_between(start_date='-1y', end_date='now')
                )
                db.session.add(sale)
                sales_list.append(sale)

        # Tüm satışları ekledikten sonra primleri hesapla
        try:
            db.session.flush() # Satışlara ID atanması için flush et
            successful_commissions = 0
            for sale in sales_list:
                if sale.id: # ID atanmışsa prim hesapla
                    if calculate_and_record_commission(sale):
                        successful_commissions += 1
                else:
                    current_app.logger.warning(f"Satış ID'si alınamadı, prim hesaplanamıyor. Ürün: {sale.product_name}")
            db.session.commit() # Satışları ve primleri commit et
            current_app.logger.info(f"{len(sales_list)} satış ve {successful_commissions} prim başarıyla eklendi.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Satış/Prim eklenirken hata: {e}", exc_info=True)
            # Devam et, diğer adımlar etkilenebilir ama denemeye değer


        current_app.logger.info("7/9: Akademi kursları, dersleri ve quizleri oluşturuluyor...")
        # Kurs kapak resimleri webden (Unsplash) çekiliyor
        course1 = Course(
            title="Modern Dijital Pazarlama Stratejileri", 
            description="SEO, SEM ve içerik pazarlamasının temellerini ve ileri düzey tekniklerini öğrenin.", 
            category="Pazarlama", 
            difficulty="Orta", 
            duration_hours=8, 
            instructor_name="Ayşe Yılmaz",
            cover_image="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop"
        )
        course2 = Course(
            title="Flask ile Web Geliştirme Sıfırdan İleri Seviyeye", 
            description="Python Flask framework'ü ile modern, ölçeklenebilir web uygulamaları geliştirin.", 
            category="Yazılım", 
            difficulty="Orta", 
            duration_hours=15, 
            instructor_name="Ahmet Kaya",
            cover_image="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=600&fit=crop"
        )
        course3 = Course(
            title="Sosyal Medya Yönetimi ve Reklamcılığı", 
            description="Markanız için etkili sosyal medya stratejileri oluşturun ve yönetin.", 
            category="Pazarlama", 
            difficulty="Başlangıç", 
            duration_hours=6, 
            instructor_name="Ayşe Yılmaz",
            cover_image="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&h=600&fit=crop"
        )
        course4 = Course(
            title="Kablosuz Ağlar", 
            description="Kablosuz ağ teknolojileri, iletişim protokolleri ve güvenlik konularını öğrenin.", 
            category="Bilişim", 
            difficulty="Orta", 
            duration_hours=12, 
            instructor_name="Yusuf Duhan",
            cover_image="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop"
        )
        db.session.add_all([course1, course2, course3, course4])
        db.session.commit() # Dersleri eklemeden önce kurs ID'leri alınmalı

        # Dersler (Course 1) - Emoji zengin içerik ve önerilen videolar ile
        l1_1_content = """<h3>🎯 Dijital Pazarlamaya Giriş</h3>
        <p>📱 Dijital pazarlama, markaların dijital kanallar üzerinden hedef kitlelerine ulaşmasını sağlayan modern bir pazarlama yaklaşımıdır.</p>
        <h4>✨ Temel Kavramlar:</h4>
        <ul>
            <li>🌐 Web pazarlama: Web siteniz üzerinden yapılan pazarlama faaliyetleri</li>
            <li>📧 E-posta pazarlama: Hedef kitleye e-posta gönderimi</li>
            <li>📱 Sosyal medya pazarlama: Platformlar üzerinden içerik paylaşımı</li>
            <li>🔍 Arama motoru optimizasyonu (SEO): Organik görünürlük artırma</li>
        </ul>
        <p>💡 Dijital pazarlama, geleneksel pazarlamadan farklı olarak ölçülebilir sonuçlar ve gerçek zamanlı geri bildirim sağlar.</p>"""
        
        l1_2_content = """<h3>🔍 SEO Temelleri: Anahtar Kelime Araştırması</h3>
        <p>📊 Anahtar kelime araştırması, SEO stratejinizin temel taşıdır. Doğru anahtar kelimeleri bulmak, web sitenizin arama motorlarında üst sıralara çıkmasını sağlar. Bu süreç, hedef kitlenizin ne aradığını anlamak ve içeriğinizi buna göre optimize etmek demektir.</p>
        
        <h4>🎯 Anahtar Kelime Araştırma Adımları:</h4>
        <ol>
            <li><strong>💭 Ürün veya Hizmetinizi Analiz Edin:</strong> Ne sunduğunuzu, kimlere hitap ettiğinizi ve benzersiz yönlerinizi belirleyin. Hedef kitleyi demografik ve psikografik özelliklerine göre segmentlere ayırın.</li>
            <li><strong>🔎 Araştırma Araçlarını Kullanın:</strong> Google Keyword Planner, Ahrefs, SEMrush, Ubersuggest gibi profesyonel araçlarla potansiyel anahtar kelimeleri keşfedin. Ücretsiz araçlar da mevcuttur (Google Trends, Answer The Public).</li>
            <li><strong>📈 Arama Hacmini ve Rekabeti Analiz Edin:</strong> Yüksek arama hacmi ama düşük rekabet olan "tatlı nokta" anahtar kelimeleri bulun. Arama hacmi, aylık ortalama arama sayısını gösterir.</li>
            <li><strong>🎨 Uzun Kuyruklu Anahtar Kelimeleri Tercih Edin:</strong> "web tasarım" yerine "İstanbul web tasarım şirketi" gibi spesifik terimler genelde daha az rekabetli ve daha yüksek dönüşüm oranına sahiptir.</li>
            <li><strong>🔗 Rakip Analizi Yapın:</strong> Başarılı rakiplerinizin hangi anahtar kelimeleri kullandığını inceleyin ve benzer stratejiler geliştirin.</li>
        </ol>
        
        <h4>📊 Anahtar Kelime Türleri:</h4>
        <ul>
            <li><strong>Kısa Kuyruk (Short Tail):</strong> 1-2 kelimeden oluşan genel terimler (örn: "web tasarım") - Yüksek rekabet</li>
            <li><strong>Uzun Kuyruk (Long Tail):</strong> 3+ kelimeden oluşan spesifik terimler (örn: "İstanbul'da profesyonel web tasarım şirketi") - Düşük rekabet, yüksek dönüşüm</li>
            <li><strong>Lokal Anahtar Kelimeler:</strong> Coğrafi konum içeren terimler (örn: "Ankara SEO uzmanı")</li>
            <li><strong>İşlem Amaçlı (Transactional):</strong> Satın alma niyeti olan terimler (örn: "satın al", "fiyat")</li>
            <li><strong>Bilgi Amaçlı (Informational):</strong> Araştırma yapan kullanıcılar için (örn: "nasıl yapılır", "nedir")</li>
        </ul>
        
        <h4>⚡ Önemli İpuçları:</h4>
        <ul>
            <li>Kullanıcı niyetini anlamak, doğru anahtar kelimeleri seçmek kadar önemlidir. Kullanıcı ne aramak istiyor?</li>
            <li>Anahtar kelime yoğunluğu %1-2 arasında tutulmalıdır. Aşırı kullanım (keyword stuffing) SEO cezalarına neden olabilir.</li>
            <li>Anahtar kelimeleri doğal bir şekilde içeriğe entegre edin. Kullanıcı deneyimi her zaman önceliklidir.</li>
            <li>Düzenli olarak anahtar kelime performansınızı takip edin ve stratejinizi güncelleyin.</li>
        </ul>
        
        <p>💡 <strong>Sonuç:</strong> Başarılı bir SEO stratejisi, doğru anahtar kelime araştırması ile başlar. Zamanınızı bu sürece ayırın ve içeriğinizi kullanıcıların gerçekten aradığı terimlerle optimize edin.</p>"""
        
        l1_3_content = """<h3>⚙️ Teknik SEO Optimizasyonu</h3>
        <p>🔧 Teknik SEO, web sitenizin arama motorları tarafından daha iyi anlaşılmasını, taranmasını ve indekslenmesini sağlayan teknik düzenlemelerdir. İçerik ne kadar iyi olursa olsun, teknik SEO eksikse arama motorları sitenizi düzgün şekilde göremez.</p>
        
        <h4>📋 Teknik SEO Kontrol Listesi:</h4>
        <ul>
            <li><strong>🚀 Sayfa Yükleme Hızı Optimizasyonu:</strong> Sayfa hızı hem kullanıcı deneyimi hem de SEO için kritiktir. Google PageSpeed Insights ile hızınızı test edin. Görsel optimizasyonu, CDN kullanımı, caching ve minification gibi teknikler uygulayın.</li>
            <li><strong>📱 Mobil Uyumluluk (Responsive Tasarım):</strong> Google'ın mobil-first yaklaşımı nedeniyle sitenizin tüm cihazlarda mükemmel görünmesi gerekir. Mobile-Friendly Test ile kontrol edin.</li>
            <li><strong>🗺️ XML Sitemap Oluşturma:</strong> Tüm sayfalarınızı içeren bir XML sitemap oluşturup Google Search Console'a gönderin. Bu, arama motorlarının sitenizi daha hızlı keşfetmesini sağlar.</li>
            <li><strong>🔗 İç Bağlantı Yapısı (Internal Linking):</strong> Sayfalarınız arasında mantıklı bir bağlantı ağı oluşturun. Bu, hem kullanıcı navigasyonunu hem de SEO'yu iyileştirir.</li>
            <li><strong>📄 Meta Etiketleri ve Title Tag Optimizasyonu:</strong> Her sayfa için benzersiz, açıklayıcı title ve meta description yazın. Title 50-60 karakter, meta description 120-150 karakter arasında olmalıdır.</li>
            <li><strong>🔒 HTTPS ve SSL Sertifikası:</strong> Güvenlik hem kullanıcılar hem de Google için önemlidir. Mutlaka SSL sertifikası kullanın.</li>
            <li><strong>📐 URL Yapısı:</strong> Temiz, okunabilir ve anahtar kelime içeren URL'ler kullanın. Örnek: "yoursite.com/urun/seo-hizmetleri"</li>
            <li><strong>🏗️ Site Yapısı ve Hiyerarşi:</strong> Mantıklı bir kategori ve sayfa yapısı oluşturun. Breadcrumb navigasyonu ekleyin.</li>
            <li><strong>🔄 301 Yönlendirmeleri:</strong> Silinen veya taşınan sayfalar için doğru yönlendirmeler yapın. 404 hatalarını düzeltin.</li>
            <li><strong>📊 Schema Markup (Yapılandırılmış Veri):</strong> JSON-LD formatında schema markup ekleyerek arama sonuçlarında zengin snippet'ler elde edin.</li>
        </ul>
        
        <h4>🔍 Teknik SEO Araçları:</h4>
        <ul>
            <li><strong>Google Search Console:</strong> İndeksleme durumu, hatalar ve performans metrikleri</li>
            <li><strong>Google PageSpeed Insights:</strong> Sayfa hızı analizi ve öneriler</li>
            <li><strong>Screaming Frog:</strong> Site genelinde teknik SEO audit'i</li>
            <li><strong>GTmetrix:</strong> Detaylı sayfa hızı analizi</li>
            <li><strong>Mobile-Friendly Test:</strong> Mobil uyumluluk kontrolü</li>
        </ul>
        
        <h4>⚠️ Yaygın Teknik SEO Hataları:</h4>
        <ul>
            <li>Çift içerik (duplicate content) sorunları</li>
            <li>Broken linkler (404 hataları)</li>
            <li>Yavaş sayfa yükleme süreleri</li>
            <li>Mobil uyumsuzluk</li>
            <li>Eksik veya yanlış meta etiketleri</li>
            <li>Robots.txt hataları</li>
        </ul>
        
        <p>💪 <strong>Sonuç:</strong> Teknik SEO, organik trafiğinizi artırmanın en önemli faktörlerinden biridir. İçerik ne kadar kaliteli olursa olsun, teknik sorunlar varsa arama motorları sitenizi düzgün şekilde değerlendiremez. Düzenli olarak teknik SEO audit'i yapın ve sorunları giderin.</p>"""
        
        l1_1 = Lesson(course=course1, order=1, title="Dijital Pazarlamaya Giriş", lesson_type="Metin", 
                     content=l1_1_content, 
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        l1_2 = Lesson(course=course1, order=2, title="SEO Temelleri: Anahtar Kelime Araştırması", lesson_type="Metin", 
                     content=l1_2_content,
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        l1_3 = Lesson(course=course1, order=3, title="Teknik SEO Optimizasyonu", lesson_type="Metin", 
                     content=l1_3_content,
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        # Quiz'ler en sona taşınıyor
        
        l1_5_content = """<h3>📝 İçerik Pazarlaması Stratejileri</h3>
        <p>İçerik pazarlaması, hedef kitlenize değerli, alakalı ve tutarlı içerikler sunarak onları çekmek ve etkileşim kurmak için kullanılan bir pazarlama yaklaşımıdır. İyi bir içerik stratejisi, markanızın otoritesini artırır ve organik trafiğinizi yükseltir.</p>
        
        <h4>🎯 İçerik Stratejisi Oluşturma:</h4>
        <ul>
            <li><strong>Hedef Kitle Analizi:</strong> İçeriğinizi kim okuyacak? Kullanıcı persona'ları oluşturun ve ihtiyaçlarını anlayın.</li>
            <li><strong>İçerik Takvimi:</strong> Haftalık veya aylık içerik planı oluşturun. Tutarlılık çok önemlidir.</li>
            <li><strong>İçerik Türleri:</strong> Blog yazıları, video içerikler, infografikler, e-kitaplar, podcast'ler, webinarlar.</li>
            <li><strong>Anahtar Kelime Entegrasyonu:</strong> SEO için içeriklerinize doğal bir şekilde anahtar kelimeler yerleştirin.</li>
        </ul>
        
        <h4>✍️ Kaliteli İçerik Yazma Teknikleri:</h4>
        <ul>
            <li><strong>Başlık Optimizasyonu:</strong> Dikkat çekici, SEO uyumlu ve değer vaat eden başlıklar kullanın.</li>
            <li><strong>Giriş Paragrafı:</strong> İlk 100 kelime kritiktir. Okuyucunun dikkatini çekin ve içeriğin değerini gösterin.</li>
            <li><strong>Okunabilirlik:</strong> Kısa paragraflar, alt başlıklar, madde işaretleri ve görseller kullanın.</li>
            <li><strong>Call-to-Action (CTA):</strong> Her içerikte net bir aksiyon çağrısı bulundurun.</li>
        </ul>
        
        <h4>📊 İçerik Dağıtımı ve Promosyon:</h4>
        <ul>
            <li><strong>Sosyal Medya Paylaşımı:</strong> İçeriğinizi tüm platformlarda paylaşın, ancak her platform için optimize edin.</li>
            <li><strong>E-posta Pazarlama:</strong> Abonelere yeni içeriklerinizi bildirin.</li>
            <li><strong>SEO Optimizasyonu:</strong> Meta açıklamalar, görsel alt etiketleri, internal linking.</li>
            <li><strong>Guest Posting:</strong> Başka sitelerde yazarak otoritenizi artırın.</li>
        </ul>
        
        <h4>📈 İçerik Performansı Ölçümü:</h4>
        <ul>
            <li>Sayfa görüntüleme sayısı</li>
            <li>Ortalama oturum süresi</li>
            <li>Hemen çıkma oranı</li>
            <li>Social share sayıları</li>
            <li>Backlink kazanımları</li>
            <li>Dönüşüm oranları</li>
        </ul>
        
        <h4>💡 İçerik Pazarlaması Best Practices:</h4>
        <ul>
            <li>Orijinal ve değerli içerik üretin (kopya içerikten kaçının)</li>
            <li>Görsel içerikler kullanın (görseller içerik performansını artırır)</li>
            <li>Hikaye anlatımı tekniklerini kullanın</li>
            <li>Kullanıcı geri bildirimlerini dinleyin ve içeriğinizi buna göre güncelleyin</li>
            <li>Long-form içerikler (2000+ kelime) genelde daha iyi performans gösterir</li>
            <li>E-A-T (Expertise, Authoritativeness, Trustworthiness) prensiplerine uyun</li>
        </ul>
        
        <p>💪 <strong>Sonuç:</strong> İçerik pazarlaması, uzun vadeli bir stratejidir. Tutarlılık, kalite ve sabırla, organik trafiğinizi ve marka otoritenizi önemli ölçüde artırabilirsiniz. İçerikleriniz, markanızın dijital dünyadaki sesi olmalıdır.</p>"""
        
        l1_4_content = l1_5_content  # İçerik pazarlaması içeriği
        l1_4 = Lesson(course=course1, order=4, title="İçerik Pazarlaması Stratejileri", lesson_type="Metin",
                     content=l1_4_content,
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        
        l1_5 = Lesson(course=course1, order=5, title="İçerik Pazarlaması Stratejileri", lesson_type="Metin", 
                     content=l1_5_content,
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        
        # YENİ DERS: Dijital Pazarlama Analitiği ve Raporlama
        l1_6_content = """<h3>📊 Dijital Pazarlama Analitiği ve Raporlama</h3>
        <p>Dijital pazarlamada başarı, verileri doğru analiz etmek ve stratejileri bu analizlere göre şekillendirmekle gelir. Bu ders, dijital pazarlama metriklerini anlama, raporlama ve analiz etme konularını kapsamlı bir şekilde ele almaktadır.</p>
        
        <h4>📈 Temel Metrikler ve KPI'lar:</h4>
        <ul>
            <li><strong>Web Sitesi Metrikleri:</strong> Sayfa görüntüleme, benzersiz ziyaretçi, oturum süresi, hemen çıkma oranı</li>
            <li><strong>Sosyal Medya Metrikleri:</strong> Takipçi sayısı, etkileşim oranı, erişim, tıklama oranı (CTR)</li>
            <li><strong>E-posta Pazarlama Metrikleri:</strong> Açılma oranı, tıklama oranı, dönüşüm oranı</li>
            <li><strong>Reklam Metrikleri:</strong> Maliyet, dönüşüm maliyeti (CPA), ROI (Yatırım Getirisi)</li>
        </ul>
        
        <h4>🔍 Analiz Araçları:</h4>
        <ul>
            <li><strong>Google Analytics:</strong> Web sitesi trafiğini analiz etme, kullanıcı davranışlarını anlama</li>
            <li><strong>Google Search Console:</strong> Arama performansı, indeksleme durumu, teknik sorunlar</li>
            <li><strong>Facebook Insights / Instagram Analytics:</strong> Sosyal medya performans analizi</li>
            <li><strong>Email Marketing Platformları:</strong> Mailchimp, Sendinblue gibi platformların analitik özellikleri</li>
        </ul>
        
        <h4>📋 Raporlama Stratejileri:</h4>
        <ul>
            <li>Haftalık, aylık ve yıllık raporlar oluşturma</li>
            <li>Görselleştirme teknikleri (grafikler, tablolar, infografikler)</li>
            <li>Stakeholder'lara sunum için hazırlık</li>
            <li>Veri odaklı karar verme süreçleri</li>
        </ul>
        
        <h4>🎯 Hedef Belirleme ve Optimizasyon:</h4>
        <p>SMART hedefler belirleme (Spesifik, Ölçülebilir, Ulaşılabilir, İlgili, Zamana Bağlı) ve bu hedeflere ulaşmak için sürekli optimizasyon yapma stratejileri.</p>
        
        <p>💡 <strong>Sonuç:</strong> Doğru analiz ve raporlama, dijital pazarlama kampanyalarınızın başarısını artırmanın en önemli faktörlerinden biridir. Verileri anlamak ve bunları aksiyona dönüştürmek, rekabet avantajı sağlar.</p>"""
        
        l1_5 = Lesson(course=course1, order=5, title="Dijital Pazarlama Analitiği ve Raporlama", lesson_type="Metin",
                     content=l1_6_content,
                     recommended_videos=json.dumps(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]))
        l1_6 = Lesson(course=course1, order=6, title="Quiz: SEO Bilgisi", lesson_type="Quiz", content="SEO temelleri hakkındaki bilgilerinizi test edin.")
        
        db.session.add_all([l1_1, l1_2, l1_3, l1_4, l1_5, l1_6])

        # Dersler (Course 2) - Flask ile Web Geliştirme
        l2_1_content = """<h3>🐍 Flask Kurulumu ve Temel Kavramlar</h3>
        <p>Flask, Python ile web uygulamaları geliştirmek için kullanılan hafif ve esnek bir framework'tür. Django'dan farklı olarak minimal bir yapıya sahiptir ve geliştiricilere daha fazla kontrol sağlar. Bu ders, Flask'ı sıfırdan öğrenmek isteyenler için temel kavramları ve kurulum sürecini kapsamlı bir şekilde ele almaktadır.</p>
        
        <h4>📦 Flask Kurulumu ve Ortam Hazırlığı:</h4>
        <p>İlk adım olarak Flask'ı kurmanız gerekiyor. Python'unuzun yüklü olduğundan emin olun (Python 3.7 veya üzeri önerilir):</p>
        <pre><code>pip install Flask</code></pre>
        
        <p><strong>Virtual Environment (Sanal Ortam) Kullanımı:</strong> Her proje için ayrı bir virtual environment oluşturmanız önerilir. Bu, projeleriniz arasında bağımlılık çatışmalarını önler:</p>
        <pre><code># Virtual environment oluşturma
python -m venv venv

# Virtual environment'ı aktif etme
# Windows için:
venv\\Scripts\\activate
# Linux/Mac için:
source venv/bin/activate

# Flask'ı kurma
pip install Flask</code></pre>
        
        <h4>🚀 İlk Flask Uygulamanızı Oluşturma:</h4>
        <p>Basit bir Flask uygulaması oluşturalım. <code>app.py</code> adında bir dosya oluşturun:</p>
        <pre><code>from flask import Flask

# Flask uygulaması oluştur
app = Flask(__name__)

# Ana sayfa route'u
@app.route('/')
def hello():
    return 'Merhaba Dünya!'

# Hakkında sayfası route'u
@app.route('/about')
def about():
    return 'Bu Flask ile oluşturulmuş bir web sitesidir.'

# Uygulamayı çalıştır
if __name__ == '__main__':
    app.run(debug=True)</code></pre>
        
        <p>Uygulamayı çalıştırmak için terminal'de şu komutu kullanın:</p>
        <pre><code>python app.py</code></pre>
        
        <p>Tarayıcınızda <code>http://127.0.0.1:5000</code> adresine giderek uygulamanızı görebilirsiniz.</p>
        
        <h4>🔑 Flask'ın Temel Kavramları:</h4>
        <ul>
            <li><strong>Route (Yol):</strong> <code>@app.route('/')</code> dekoratörü ile tanımlanır. URL'lerin hangi fonksiyonlara bağlanacağını belirler. Örneğin, <code>/</code> ana sayfayı, <code>/about</code> hakkında sayfasını temsil eder.</li>
            <li><strong>View Function:</strong> Route'a bağlanan Python fonksiyonlarıdır. Bu fonksiyonlar, kullanıcının isteğine göre yanıt döndürür.</li>
            <li><strong>Template:</strong> HTML şablonları (Jinja2 ile). Dinamik içerik oluşturmak için kullanılır. <code>templates/</code> klasöründe saklanır.</li>
            <li><strong>Request/Response:</strong> HTTP istekleri ve yanıtları. Flask, gelen istekleri işler ve uygun yanıtları döndürür.</li>
            <li><strong>Blueprint:</strong> Uygulamayı modüler hale getirmek için kullanılır. Büyük projelerde kod organizasyonu için kritiktir.</li>
            <li><strong>Static Files:</strong> CSS, JavaScript ve resim dosyaları için <code>static/</code> klasörü kullanılır.</li>
        </ul>
        
        <h4>📁 Flask Proje Yapısı:</h4>
        <p>İyi organize edilmiş bir Flask projesi şu şekilde görünür:</p>
        <pre><code>my_flask_app/
    ├── app.py              # Ana uygulama dosyası
    ├── templates/          # HTML şablonları
    │   ├── base.html
    │   └── index.html
    ├── static/             # Statik dosyalar (CSS, JS, resimler)
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── venv/               # Virtual environment
    └── requirements.txt     # Bağımlılıklar</code></pre>
        
        <h4>🔧 Debug Mode (Hata Ayıklama Modu):</h4>
        <p><code>debug=True</code> parametresi, geliştirme sırasında hataları görmenizi ve otomatik yeniden yükleme sağlar. Ancak, üretim ortamında <strong>ASLA</strong> debug modunu açık bırakmayın:</p>
        <pre><code>if __name__ == '__main__':
    app.run(debug=True)  # Sadece geliştirme için</code></pre>
        
        <p>💡 <strong>Sonuç:</strong> Flask, küçük projelerden büyük uygulamalara kadar ölçeklenebilir bir yapıya sahiptir. Minimalist yaklaşımı sayesinde, sadece ihtiyacınız olan özellikleri ekleyerek esnek ve güçlü web uygulamaları geliştirebilirsiniz.</p>"""
        
        l2_2_content = """<h3>🎨 Jinja2 Şablon Motoru</h3>
        <p>Jinja2, Flask'ın varsayılan şablon motorudur. Python benzeri bir sözdizimi kullanarak dinamik HTML sayfaları oluşturmanızı sağlar. Bu ders, Jinja2'nin temel özelliklerini ve pratik kullanım örneklerini kapsamaktadır.</p>
        
        <h4>📝 Temel Jinja2 Sözdizimi ve Kullanımı:</h4>
        <p>Jinja2, HTML içinde Python benzeri ifadeler kullanmanıza olanak tanır:</p>
        
        <h5>1. Değişkenler (Variables):</h5>
        <p>Değişkenleri görüntülemek için çift süslü parantez kullanılır:</p>
        <pre><code><!-- Template dosyasında -->
<h1>Hoş geldin, {{ kullanici_adi }}!</h1>
<p>Bugünün tarihi: {{ tarih }}</p></code></pre>
        
        <pre><code># Python dosyasında (app.py)
@app.route('/')
def index():
    return render_template('index.html', 
                         kullanici_adi='Ahmet',
                         tarih='2025-01-15')</code></pre>
        
        <h5>2. Bloklar (Blocks):</h5>
        <p>Template kalıtımı için bloklar kullanılır:</p>
        <pre><code><!-- base.html -->
<html>
<head><title>{% block title %}Varsayılan Başlık{% endblock %}</title></head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- index.html -->
{% extends "base.html" %}
{% block title %}Ana Sayfa{% endblock %}
{% block content %}
    <h1>Ana Sayfa İçeriği</h1>
{% endblock %}</code></pre>
        
        <h5>3. Döngüler (Loops):</h5>
        <p>Listeler üzerinde döngü yapmak için:</p>
        <pre><code><!-- Template -->
<ul>
{% for kullanici in kullanicilar %}
    <li>{{ kullanici.isim }} - {{ kullanici.email }}</li>
{% endfor %}
</ul>

<!-- Python -->
@app.route('/kullanicilar')
def kullanicilar():
    kullanici_listesi = [
        {'isim': 'Ahmet', 'email': 'ahmet@example.com'},
        {'isim': 'Ayşe', 'email': 'ayse@example.com'}
    ]
    return render_template('kullanicilar.html', kullanicilar=kullanici_listesi)</code></pre>
        
        <h5>4. Koşullar (Conditionals):</h5>
        <pre><code><!-- Template -->
{% if kullanici %}
    <p>Hoş geldin, {{ kullanici.isim }}!</p>
{% else %}
    <p>Lütfen giriş yapın.</p>
{% endif %}

{% if yas >= 18 %}
    <p>Yetişkin içeriği</p>
{% elif yas >= 13 %}
    <p>Genç içeriği</p>
{% else %}
    <p>Çocuk içeriği</p>
{% endif %}</code></pre>
        
        <h4>🔄 Template Kalıtımı ve Organizasyon:</h4>
        <p>Base template oluşturup diğer sayfaları extend ederek kod tekrarını önleyebilirsiniz:</p>
        <pre><code><!-- templates/base.html -->
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}KUWAMEDYA{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}">Ana Sayfa</a>
        <a href="{{ url_for('about') }}">Hakkında</a>
    </nav>
    
    {% block content %}{% endblock %}
    
    <footer>
        <p>&copy; 2025 KUWAMEDYA</p>
    </footer>
</body>
</html>

<!-- templates/index.html -->
{% extends "base.html" %}
{% block title %}Ana Sayfa - KUWAMEDYA{% endblock %}
{% block content %}
    <h1>Hoş Geldiniz!</h1>
    <p>Bu ana sayfa içeriğidir.</p>
{% endblock %}</code></pre>
        
        <h4>🔧 Filtreler (Filters):</h4>
        <p>Jinja2, değişkenleri dönüştürmek için filtreler sunar:</p>
        <pre><code>{{ isim | upper }}          <!-- Büyük harfe çevir -->
{{ metin | capitalize }}    <!-- İlk harfi büyüt -->
{{ tarih | date }}          <!-- Tarih formatla -->
{{ uzun_metin | truncate(50) }}  <!-- Metni kısalt -->
{{ liste | length }}        <!-- Liste uzunluğu -->
{{ deger | default('Varsayılan') }}  <!-- Varsayılan değer --></code></pre>
        
        <h4>🛡️ Güvenlik ve XSS Koruması:</h4>
        <p>Jinja2, otomatik olarak HTML escape yapar ve XSS saldırılarına karşı koruma sağlar:</p>
        <pre><code><!-- Güvenli - Otomatik escape -->
<p>{{ kullanici_girdisi }}</p>

<!-- Güvenli değil - Manuel escape kapatma -->
<p>{{ kullanici_girdisi | safe }}</p>  <!-- Sadece güvendiğiniz içerik için kullanın --></code></pre>
        
        <h4>📁 Template Dosyalarını Organize Etme:</h4>
        <p>Büyük projelerde template'leri organize etmek için klasör yapısı:</p>
        <pre><code>templates/
    ├── base.html           # Ana şablon
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── admin/
    │   └── dashboard.html
    └── partials/
        ├── header.html
        └── footer.html</code></pre>
        
        <p>💡 <strong>Sonuç:</strong> Jinja2, Flask uygulamalarında dinamik ve güvenli HTML sayfaları oluşturmanın en güçlü yöntemidir. Template kalıtımı, filtreler ve makrolar sayesinde, kod tekrarını önleyerek temiz ve bakımı kolay şablonlar oluşturabilirsiniz.</p>"""
        
        l2_3_content = """<h3>📋 Flask WTForms ile Form Yönetimi</h3>
        <p>WTForms, Flask uygulamalarında form oluşturma ve validasyon için güçlü bir kütüphanedir.</p>
        
        <h4>📦 Kurulum:</h4>
        <pre><code>pip install Flask-WTF</code></pre>
        
        <h4>📝 Form Sınıfı Oluşturma:</h4>
        <pre><code>from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField('İsim', validators=[DataRequired()])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    submit = SubmitField('Gönder')</code></pre>
        
        <h4>🛡️ CSRF Koruması:</h4>
        <p>Flask-WTF otomatik olarak CSRF token üretir ve doğrular. Secret key ayarlamanız gerekir:</p>
        <pre><code>app.config['SECRET_KEY'] = 'gizli-anahtar'</code></pre>
        
        <p>💡 WTForms, güvenli ve kullanıcı dostu formlar oluşturmanızı sağlar.</p>"""
        
        l2_1 = Lesson(course=course2, order=1, title="Flask Kurulumu ve Temel Kavramlar", lesson_type="Metin", content=l2_1_content)
        l2_2 = Lesson(course=course2, order=2, title="Jinja2 Şablon Motoru", lesson_type="Metin", content=l2_2_content)
        l2_3 = Lesson(course=course2, order=3, title="Flask WTForms ile Form Yönetimi", lesson_type="Metin", content=l2_3_content)
        
        l2_4_content = """<h3>🗄️ SQLAlchemy ORM ve Veritabanı İlişkileri</h3>
        <p>SQLAlchemy, Python için en popüler ORM (Object-Relational Mapping) kütüphanesidir. Veritabanı işlemlerini Python objeleri ile yapmanızı sağlar. Bu, SQL sorguları yazmak yerine Python kodları kullanarak veritabanı işlemlerini gerçekleştirmenize olanak tanır.</p>
        
        <h4>📦 Kurulum ve Temel Yapılandırma:</h4>
        <p>Flask-SQLAlchemy'yi kurarak başlayalım:</p>
        <pre><code>pip install Flask-SQLAlchemy</code></pre>
        
        <p>Flask uygulamanıza SQLAlchemy'yi entegre edin:</p>
        <pre><code>from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)</code></pre>
        
        <h4>🔗 Model Tanımlama ve Temel Yapı:</h4>
        <p>Model, veritabanı tablosunu temsil eden bir Python sınıfıdır. Her sınıf, bir tablo olur ve her özellik, bir sütun olur:</p>
        <pre><code>from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'&lt;User {self.username}&gt;'</code></pre>
        
        <h4>🔗 İlişki Türleri ve Kullanımı:</h4>
        <p>SQLAlchemy, farklı ilişki türlerini destekler:</p>
        
        <h5>One-to-Many İlişki:</h5>
        <pre><code>class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)</code></pre>
        
        <h5>Many-to-Many İlişki:</h5>
        <pre><code># İlişki tablosu
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)</code></pre>
        
        <h4>💾 Veritabanı İşlemleri:</h4>
        <p>SQLAlchemy ile temel CRUD (Create, Read, Update, Delete) işlemleri:</p>
        <pre><code># Oluşturma (Create)
new_user = User(username='ahmet', email='ahmet@example.com')
db.session.add(new_user)
db.session.commit()

# Okuma (Read)
user = User.query.filter_by(username='ahmet').first()
all_users = User.query.all()

# Güncelleme (Update)
user.email = 'yeni@example.com'
db.session.commit()

# Silme (Delete)
db.session.delete(user)
db.session.commit()</code></pre>
        
        <h4>🔍 Sorgulama Teknikleri:</h4>
        <ul>
            <li><strong>filter_by():</strong> Basit filtreleme için <code>User.query.filter_by(username='ahmet').first()</code></li>
            <li><strong>filter():</strong> Daha gelişmiş sorgular için <code>User.query.filter(User.email.like('%@gmail.com')).all()</code></li>
            <li><strong>order_by():</strong> Sıralama için <code>User.query.order_by(User.created_at.desc()).all()</code></li>
            <li><strong>limit():</strong> Sonuç sayısını sınırlama için <code>User.query.limit(10).all()</code></li>
        </ul>
        
        <h4>🛡️ Güvenlik ve En İyi Uygulamalar:</h4>
        <ul>
            <li><strong>Veritabanı Bağlantı Yönetimi:</strong> Bağlantıların doğru şekilde kapatılması</li>
            <li><strong>SQL Injection Koruması:</strong> SQLAlchemy otomatik olarak parametreli sorgular kullanır</li>
            <li><strong>Transaction Yönetimi:</strong> <code>db.session.rollback()</code> ile hata durumunda geri alma</li>
            <li><strong>Index Kullanımı:</strong> Sık sorgulanan sütunlara index ekleme</li>
        </ul>
        
        <p>💡 <strong>Sonuç:</strong> SQLAlchemy, Flask uygulamalarında veritabanı işlemlerini basitleştirir ve güvenli hale getirir. Python objeleri ile çalışarak, SQL bilgisi olmadan da güçlü veritabanı uygulamaları geliştirebilirsiniz.</p>"""
        
        l2_4 = Lesson(course=course2, order=4, title="SQLAlchemy ORM ve Veritabanı İlişkileri", lesson_type="Metin", content=l2_4_content)
        l2_5 = Lesson(course=course2, order=5, title="Flask Blueprints ve Uygulama Yapısı", lesson_type="Metin", content="""<h3>🏗️ Flask Blueprints ve Uygulama Yapısı</h3>
        <p>Blueprints, Flask uygulamalarını modüler hale getirmek için kullanılır. Büyük projelerde kod organizasyonu için kritiktir.</p>
        
        <h4>📁 Modüler Yapı:</h4>
        <p>Her blueprint, farklı bir özellik setini temsil eder (auth, admin, api vb.)</p>
        
        <h4>💡 Avantajlar:</h4>
        <ul>
            <li>Kod organizasyonu</li>
            <li>Yeniden kullanılabilirlik</li>
            <li>Kolay bakım</li>
            <li>Ekip çalışmasına uygunluk</li>
        </ul>
        
        <p>💡 Blueprints, Flask uygulamalarını ölçeklenebilir hale getirir.</p>""")
        l2_6 = Lesson(course=course2, order=6, title="Modern Web Sitesi Tasarımı ve Kullanıcı Deneyimi", lesson_type="Metin", content="""<h3>🎨 Modern Web Sitesi Tasarımı ve Kullanıcı Deneyimi (UX/UI)</h3>
        <p>Modern web geliştirmede, kullanıcı deneyimi ve arayüz tasarımı teknik geliştirmeler kadar önemlidir. Bu ders, profesyonel, kullanıcı dostu ve dönüşüm odaklı web siteleri tasarlamak için gerekli tüm prensipleri kapsamaktadır.</p>
        
        <h4>🎯 UX/UI Tasarım Prensipleri:</h4>
        <ul>
            <li><strong>Kullanıcı Odaklı Tasarım:</strong> Kullanıcının ihtiyaçlarını anlamak ve tasarımı buna göre şekillendirmek. Persona oluşturma, kullanıcı araştırmaları ve kullanıcı yolculuğu haritalama teknikleri.</li>
            <li><strong>Görsel Hiyerarşi:</strong> Önemli bilgileri öne çıkarmak için tipografi, renk, boşluk ve boyut kullanımı. F-pattern ve Z-pattern okuma alışkanlıkları.</li>
            <li><strong>Konsistens ve Tutarlılık:</strong> Tüm sayfalarda aynı tasarım dili, renk paleti ve bileşen kullanımı. Marka kimliğinin korunması.</li>
            <li><strong>Erişilebilirlik (Accessibility):</strong> WCAG 2.1 standartlarına uyum, renk kontrastı, klavye navigasyonu, ekran okuyucu desteği.</li>
            <li><strong>Responsive Tasarım:</strong> Mobil-first yaklaşım, breakpoint'ler, esnek grid sistemleri ve görsel uyumluluk.</li>
        </ul>
        
        <h4>📐 Modern Layout Teknikleri:</h4>
        <ul>
            <li><strong>Grid Sistemleri:</strong> CSS Grid ve Flexbox kullanımı ile esnek ve modern yerleşimler.</li>
            <li><strong>Card-Based Tasarım:</strong> Bilgileri kartlar halinde düzenleyerek görsel düzen ve okunabilirlik sağlama.</li>
            <li><strong>Hero Section:</strong> Etkileyici giriş bölümleri tasarlama, CTA (Call-to-Action) yerleşimi.</li>
            <li><strong>White Space Kullanımı:</strong> Boşlukların tasarımda rolü, nefes alan sayfalar oluşturma.</li>
        </ul>
        
        <h4>🎨 Renk Teorisi ve Tipografi:</h4>
        <ul>
            <li><strong>Renk Paleti Seçimi:</strong> Marka renkleri, ana renkler, vurgu renkleri ve arka plan renkleri. Renk psikolojisi ve kültürel anlamları.</li>
            <li><strong>Tipografi Hiyerarşisi:</strong> Başlık, alt başlık ve metin boyutları. Font ailesi seçimi (serif, sans-serif, monospace). Google Fonts ve web font kullanımı.</li>
            <li><strong>Okunabilirlik:</strong> Satır yüksekliği (line-height), harf aralığı (letter-spacing) ve paragraf boşlukları.</li>
        </ul>
        
        <h4>⚡ Performans ve Optimizasyon:</h4>
        <ul>
            <li><strong>Görsel Optimizasyonu:</strong> Görsel sıkıştırma, lazy loading, WebP formatı kullanımı, responsive images.</li>
            <li><strong>Hızlı Yükleme:</strong> Minification, CSS/JS birleştirme, CDN kullanımı, caching stratejileri.</li>
            <li><strong>Core Web Vitals:</strong> LCP (Largest Contentful Paint), FID (First Input Delay), CLS (Cumulative Layout Shift) optimizasyonu.</li>
        </ul>
        
        <h4>🔧 Modern CSS Teknikleri:</h4>
        <ul>
            <li><strong>CSS Variables:</strong> Tema yönetimi, dinamik renk değişimi, dark mode desteği.</li>
            <li><strong>Animasyonlar ve Geçişler:</strong> Smooth transitions, hover efektleri, micro-interactions.</li>
            <li><strong>Modern CSS Özellikleri:</strong> CSS Grid, Flexbox, Custom Properties, Container Queries.</li>
        </ul>
        
        <h4>📱 Mobil Deneyim:</h4>
        <ul>
            <li><strong>Touch-Friendly Tasarım:</strong> Buton boyutları, dokunma alanları, gestürler.</li>
            <li><strong>Mobil Navigasyon:</strong> Hamburger menü, bottom navigation, sticky header.</li>
            <li><strong>Progressive Web App (PWA):</strong> Offline çalışma, app-like deneyim.</li>
        </ul>
        
        <h4>🎯 Dönüşüm Optimizasyonu (CRO):</h4>
        <ul>
            <li><strong>CTA Butonları:</strong> Güçlü, görünür ve net call-to-action butonları tasarlama.</li>
            <li><strong>Form Tasarımı:</strong> Kullanıcı dostu formlar, validasyon mesajları, progress göstergeleri.</li>
            <li><strong>Güven İşaretleri:</strong> Testimonials, sertifikalar, güvenlik rozetleri.</li>
            <li><strong>A/B Testing:</strong> Farklı tasarım varyasyonlarını test etme ve optimize etme.</li>
        </ul>
        
        <h4>🛠️ Popüler Tasarım Araçları ve Framework'ler:</h4>
        <ul>
            <li><strong>Design Tools:</strong> Figma, Adobe XD, Sketch kullanımı ve prototipleme.</li>
            <li><strong>CSS Framework'leri:</strong> Bootstrap 5, Tailwind CSS, Material UI avantajları ve kullanım alanları.</li>
            <li><strong>Component Libraries:</strong> Hazır bileşen kütüphaneleri kullanımı ve özelleştirme.</li>
        </ul>
        
        <h4>💡 Best Practices:</h4>
        <ul>
            <li>Kullanıcı testleri yapma ve geri bildirimleri değerlendirme</li>
            <li>Erişilebilirlik standartlarına uyum (WCAG 2.1 Level AA)</li>
            <li>Cross-browser uyumluluk testleri</li>
            <li>SEO-friendly HTML yapısı</li>
            <li>Performans monitoring ve sürekli optimizasyon</li>
        </ul>
        
        <p>💪 <strong>Sonuç:</strong> Modern web tasarımı, teknik bilgi ve yaratıcılığın birleşimidir. Kullanıcı deneyimini ön planda tutarak, performanslı, erişilebilir ve dönüşüm odaklı web siteleri oluşturabilirsiniz. Unutmayın: En iyi tasarım, kullanıcının ihtiyaçlarını en iyi şekilde karşılayan tasarımdır.</p>""")
        # Yeni Ders: Kurumsal Kimlik ve İmaj Planlama
        l2_7_content = """<h3>🎨 Kurumsal Kimlik ve İmaj Planlama</h3>
        <p>Kurumsal kimlik, bir işletmenin görsel ve duygusal temsilidir. Marka kimliği, logo, renk paleti, tipografi ve genel tasarım dili ile müşterilerinizin zihninde nasıl bir izlenim bıraktığınızı belirler. Bu ders, profesyonel bir kurumsal kimlik oluşturmanın tüm adımlarını ve en iyi uygulamalarını kapsamaktadır.</p>
        
        <h4>🎯 Kurumsal Kimlik Nedir?</h4>
        <p>Kurumsal kimlik, şirketinizin görsel kimliğinin tüm unsurlarını içeren kapsamlı bir sistemdir:</p>
        <ul>
            <li><strong>Logo:</strong> Şirketinizin görsel simgesi ve en önemli kimlik öğesi</li>
            <li><strong>Renk Paleti:</strong> Marka renkleri ve bunların kullanım kuralları</li>
            <li><strong>Tipografi:</strong> Font seçimi ve metin stilleri</li>
            <li><strong>Görsel Dil:</strong> Fotoğraf stili, illüstrasyonlar ve görsel öğeler</li>
            <li><strong>Tone of Voice:</strong> Yazılı ve sözlü iletişimdeki ses tonu</li>
        </ul>
        
        <h4>📋 Kurumsal Kimlik Rehberi (Brand Guidelines) Oluşturma:</h4>
        <p>Profesyonel bir kurumsal kimlik için mutlaka bir rehber oluşturmalısınız:</p>
        
        <h5>1. Logo Kullanım Kuralları:</h5>
        <ul>
            <li>Logo'nun minimum ve maksimum boyutları</li>
            <li>Logo'nun yasak kullanım alanları (örneğin, çok küçük boyutlarda)</li>
            <li>Logo'nun renkli, siyah-beyaz ve ters renk versiyonları</li>
            <li>Logo çevresindeki minimum boşluk alanı (clear space)</li>
        </ul>
        
        <h5>2. Renk Paleti Tanımlama:</h5>
        <ul>
            <li><strong>Ana Renkler:</strong> Markanızın temel renkleri (genelde 2-3 renk)</li>
            <li><strong>İkincil Renkler:</strong> Destekleyici renkler</li>
            <li><strong>Nötr Renkler:</strong> Metin ve arka plan için kullanılan renkler</li>
            <li>Her rengin CMYK, RGB, HEX ve Pantone kodları</li>
        </ul>
        
        <h5>3. Tipografi Sistemi:</h5>
        <ul>
            <li>Ana başlık fontu (Heading font)</li>
            <li>Gövde metin fontu (Body font)</li>
            <li>Font boyutları ve hiyerarşisi</li>
            <li>Satır yüksekliği (line-height) ve harf aralığı (letter-spacing) kuralları</li>
        </ul>
        
        <h5>4. Görsel Stil Tanımlama:</h5>
        <ul>
            <li>Fotoğraf stili (doğal, profesyonel, minimalist vb.)</li>
            <li>İllüstrasyon stili (varsa)</li>
            <li>Grafik elementler (ikonlar, şekiller vb.)</li>
            <li>Görsel filtreleri ve efektleri</li>
        </ul>
        
        <h4>💼 İmaj Planlama Stratejisi:</h4>
        <p>Kurumsal imajınızı planlarken şu adımları takip edin:</p>
        
        <h5>1. Hedef Kitle Analizi:</h5>
        <ul>
            <li>Kimlerle iletişim kuruyorsunuz?</li>
            <li>Hedef kitlenizin değerleri ve beklentileri nelerdir?</li>
            <li>Rakipleriniz nasıl konumlanmış?</li>
        </ul>
        
        <h5>2. Marka Kişiliği Belirleme:</h5>
        <ul>
            <li><strong>Özellikler:</strong> Profesyonel, dost canlısı, yenilikçi, güvenilir vb.</li>
            <li><strong>Değerler:</strong> Şirketinizin temel değerleri</li>
            <li><strong>Farklılaşma:</strong> Rakiplerinizden sizi ayıran özellikler</li>
        </ul>
        
        <h5>3. Marka Hikayesi Oluşturma:</h5>
        <ul>
            <li>Şirketinizin kuruluş hikayesi</li>
            <li>Misyon ve vizyon</li>
            <li>Müşterilere verdiğiniz vaat</li>
        </ul>
        
        <h4>🎨 Logo Tasarım Prensipleri:</h4>
        <ul>
            <li><strong>Basitlik:</strong> Karmaşık logolar unutulur, basit logolar hatırlanır</li>
            <li><strong>Özgünlük:</strong> Rakiplerinizden farklı ve benzersiz olmalı</li>
            <li><strong>Ölçeklenebilirlik:</strong> Hem küçük hem büyük boyutlarda çalışmalı</li>
            <li><strong>Zamanlılık:</strong> Trend'lerden bağımsız, uzun ömürlü olmalı</li>
            <li><strong>Uygunluk:</strong> Sektörünüze ve hedef kitlenize uygun olmalı</li>
        </ul>
        
        <h4>📱 Dijital Ortamda Kurumsal Kimlik:</h4>
        <ul>
            <li><strong>Web Sitesi:</strong> Tüm görsel öğelerin tutarlı kullanımı</li>
            <li><strong>Sosyal Medya:</strong> Profil fotoğrafları, kapak görselleri ve içerik tasarımı</li>
            <li><strong>E-posta:</strong> E-posta şablonları ve imza tasarımları</li>
            <li><strong>Dijital Reklamlar:</strong> Banner ve görsel reklam tasarımları</li>
        </ul>
        
        <h4>📄 Basılı Materyallerde Kurumsal Kimlik:</h4>
        <ul>
            <li>Kartvizitler</li>
            <li>Antetli kağıtlar ve zarf tasarımları</li>
            <li>Broşürler ve kataloglar</li>
            <li>Ambalaj tasarımları</li>
            <li>Yönlendirme tabelaları</li>
        </ul>
        
        <h4>🔄 Kurumsal Kimlik Güncelleme:</h4>
        <p>Zaman zaman kurumsal kimliğinizi güncellemeniz gerekebilir:</p>
        <ul>
            <li>Şirket değişiklikleri (birleşme, satın alma vb.)</li>
            <li>Pazar değişiklikleri</li>
            <li>Eski görünümün artık hedef kitleye uymaması</li>
            <li>Yeni teknolojiler ve trendler</li>
        </ul>
        <p><strong>Önemli:</strong> Güncelleme yaparken mevcut marka değerini korumak ve yumuşak bir geçiş sağlamak kritiktir.</p>
        
        <h4>💡 En İyi Uygulamalar:</h4>
        <ul>
            <li>Kurumsal kimlik rehberinizi her zaman güncel tutun</li>
            <li>Tüm ekibinizle rehberi paylaşın ve eğitim verin</li>
            <li>Dışarıdan tasarımcı çalıştırıyorsanız, rehberi mutlaka paylaşın</li>
            <li>Düzenli olarak marka tutarlılığını kontrol edin</li>
            <li>Müşteri geri bildirimlerini dinleyin ve gerektiğinde güncellemeler yapın</li>
        </ul>
        
        <p>💪 <strong>Sonuç:</strong> Güçlü bir kurumsal kimlik, müşterilerinizin sizinle ilk temasından itibaren profesyonel bir izlenim edinmesini sağlar. Tutarlı ve iyi planlanmış bir kurumsal kimlik, marka değerinizi artırır ve uzun vadede rekabet avantajı sağlar. Unutmayın: Kurumsal kimlik, sadece görsel öğeler değil, aynı zamanda markanızın tüm duygusal ve algısal temsilidir.</p>"""
        
        l2_7 = Lesson(course=course2, order=7, title="Kurumsal Kimlik ve İmaj Planlama", lesson_type="Metin", content=l2_7_content)
        l2_8 = Lesson(course=course2, order=8, title="Quiz: Flask ve Web Geliştirme Bilgisi", lesson_type="Quiz", content="Flask ve web geliştirme konularındaki bilginizi test edin.")
        db.session.add_all([l2_1, l2_2, l2_3, l2_4, l2_5, l2_6, l2_7, l2_8])

        # Dersler (Course 3) - Sosyal Medya Yönetimi
        l3_1_content = """<h3>📱 Sosyal Medya Platformları ve Hedef Kitle</h3>
        <p>Sosyal medya pazarlama, markanızı sosyal platformlarda görünür kılmak ve hedef kitlenizle etkileşim kurmak için kritik bir araçtır. Her platformun kendine özgü özellikleri ve kullanıcı demografisi vardır.</p>
        
        <h4>🌟 Ana Sosyal Medya Platformları:</h4>
        <ul>
            <li><strong>Facebook:</strong> Geniş kitle, 25-65 yaş arası, tüm sektörler için uygun</li>
            <li><strong>Instagram:</strong> Görsel odaklı, 18-34 yaş, e-ticaret ve lifestyle markaları</li>
            <li><strong>LinkedIn:</strong> B2B, profesyonel ağ, işletmeler ve kariyer</li>
            <li><strong>Twitter:</strong> Anlık haberler, güncel konular, 18-49 yaş</li>
            <li><strong>TikTok:</strong> Genç kitle, kısa video içerik, 16-24 yaş</li>
            <li><strong>YouTube:</strong> Video içerik, eğitim ve eğlence, tüm yaş grupları</li>
        </ul>
        
        <h4>🎯 Hedef Kitle Belirleme:</h4>
        <ul>
            <li>Demografik analiz (yaş, cinsiyet, lokasyon)</li>
            <li>Psikografik özellikler (ilgi alanları, değerler)</li>
            <li>Davranışsal veriler (alışveriş alışkanlıkları)</li>
            <li>Platform kullanım alışkanlıkları</li>
        </ul>
        
        <p>💡 Doğru platform seçimi ve hedef kitle analizi, sosyal medya başarınızın temelidir.</p>"""
        
        l3_2_content = """<h3>✨ Etkili İçerik Oluşturma</h3>
        <p>Sosyal medyada başarılı olmak için içeriklerinizin yaratıcı, alakalı ve etkileşim odaklı olması gerekir.</p>
        
        <h4>📝 İçerik Planlama:</h4>
        <ul>
            <li>İçerik takvimi oluşturun</li>
            <li>Marka sesinizi ve tonunuzu belirleyin</li>
            <li>Çeşitli içerik formatları kullanın (görsel, video, carousel)</li>
            <li>Hashtag stratejisi geliştirin</li>
        </ul>
        
        <h4>🎨 Görsel İçerik İpuçları:</h4>
        <ul>
            <li>Yüksek kaliteli görseller kullanın</li>
            <li>Marka renklerinize uygun tasarımlar</li>
            <li>Okunabilir fontlar ve metinler</li>
            <li>Mobil öncelikli tasarım</li>
        </ul>
        
        <p>💡 İçerikleriniz hem bilgilendirici hem de eğlenceli olmalıdır.</p>"""
        
        l3_3_content = """<h3>📢 Sosyal Medya Reklam Kampanyaları</h3>
        <p>Organik içerik yeterli olmayabilir. Reklam kampanyaları ile hedef kitlenize daha etkili ulaşabilirsiniz.</p>
        
        <h4>💰 Platform Reklam Seçenekleri:</h4>
        <ul>
            <li><strong>Facebook Ads:</strong> Detaylı hedefleme, çeşitli formatlar</li>
            <li><strong>Instagram Ads:</strong> Görsel odaklı, Stories ve Reels reklamları</li>
            <li><strong>LinkedIn Ads:</strong> B2B hedefleme, profesyonel ağ</li>
            <li><strong>Twitter Ads:</strong> Trend takibi, anlık etkileşim</li>
        </ul>
        
        <h4>📊 Kampanya Optimizasyonu:</h4>
        <ul>
            <li>A/B testleri yapın</li>
            <li>Metrikleri düzenli takip edin</li>
            <li>Hedef kitleyi optimize edin</li>
            <li>Bütçe yönetimi yapın</li>
        </ul>
        
        <p>💡 Başarılı reklam kampanyaları, sürekli test ve optimizasyon gerektirir.</p>"""
        
        l3_1 = Lesson(course=course3, order=1, title="Sosyal Medya Platformları ve Hedef Kitle", lesson_type="Metin", content=l3_1_content)
        l3_2 = Lesson(course=course3, order=2, title="Etkili İçerik Oluşturma", lesson_type="Metin", content=l3_2_content)
        l3_3 = Lesson(course=course3, order=3, title="Sosyal Medya Reklam Kampanyaları", lesson_type="Metin", content=l3_3_content)
        l3_4 = Lesson(course=course3, order=4, title="Quiz: Sosyal Medya Yönetimi Bilgisi", lesson_type="Quiz", content="Sosyal medya yönetimi konularındaki bilginizi test edin.")
        db.session.add_all([l3_1, l3_2, l3_3, l3_4])

        db.session.commit() # Ders ID'leri alınmalı

        # Quizler - 20 soruluk quizler (18 doğru gerekiyor)
        quiz1_questions = json.dumps([
            {"question": "Aşağıdakilerden hangisi On-Page SEO faktörü değildir?", "options": ["Meta Açıklama", "Başlık Etiketi (Title Tag)", "Backlink Sayısı", "İçerik Kalitesi"], "correct_index": 2},
            {"question": "Anahtar kelime yoğunluğu (keyword density) ne anlama gelir?", "options": ["Anahtar kelimenin arama hacmi", "Anahtar kelimenin metin içindeki geçme sıklığı oranı", "Anahtar kelimenin rekabet düzeyi", "Anahtar kelimenin tıklama başına maliyeti"], "correct_index": 1},
            {"question": "HTTP 301 yönlendirmesi ne için kullanılır?", "options": ["Sayfa geçici olarak taşındığında", "Sayfa kalıcı olarak taşındığında", "Sayfa bulunamadığında", "Sunucu hatası olduğunda"], "correct_index": 1},
            {"question": "SEO'da 'long-tail keyword' nedir?", "options": ["Çok uzun URL yapısı", "3-4 kelimeden oluşan spesifik anahtar kelimeler", "Kısa ve genel anahtar kelimeler", "Teknik terimler"], "correct_index": 1},
            {"question": "XML sitemap'in temel amacı nedir?", "options": ["Sayfa görselleştirmesi", "Arama motorlarına site yapısını bildirmek", "Kullanıcı navigasyonu", "SEO puanı artırma"], "correct_index": 1},
            {"question": "Meta description'ın ideal karakter uzunluğu nedir?", "options": ["50-60 karakter", "120-150 karakter", "200-250 karakter", "300+ karakter"], "correct_index": 1},
            {"question": "H1 etiketi sayfada kaç kez kullanılmalıdır?", "options": ["Sınırsız", "Sadece 1 kez", "2-3 kez", "Sayfa başına 5 kez"], "correct_index": 1},
            {"question": "Internal linking nedir?", "options": ["Dış sitelere bağlantı verme", "Kendi siteniz içindeki sayfalar arası bağlantı", "Sosyal medya paylaşımları", "E-posta pazarlama"], "correct_index": 1},
            {"question": "Page Speed (sayfa hızı) SEO için neden önemlidir?", "options": ["Sadece kullanıcı deneyimi için", "Hem kullanıcı deneyimi hem de sıralama faktörü", "Sadece mobil için", "Hiç önemli değil"], "correct_index": 1},
            {"question": "Canonical URL nedir?", "options": ["Ana sayfa URL'si", "Tekrarlanan içeriği belirtmek için kullanılan URL", "Erişilemeyen URL", "Güvenli URL"], "correct_index": 1},
            {"question": "Schema markup (yapılandırılmış veri) ne işe yarar?", "options": ["Sayfa hızını artırır", "Arama motorlarına içeriği daha iyi anlatır", "Backlink sayısını artırır", "Sosyal medya paylaşımlarını artırır"], "correct_index": 1},
            {"question": "Alt text (alternatif metin) hangi SEO unsuruna yardımcı olur?", "options": ["Sayfa hızı", "Görsel SEO ve erişilebilirlik", "Backlink oluşturma", "Meta açıklama"], "correct_index": 1},
            {"question": "Dofollow link nedir?", "options": ["Link juice geçiren link", "Link juice geçirmeyen link", "Broken link", "Internal link"], "correct_index": 0},
            {"question": "Mobile-first indexing nedir?", "options": ["Mobil cihazlar için özel site", "Google'ın önce mobil versiyonu indekslemesi", "Mobil uygulama geliştirme", "Sadece mobil arama"], "correct_index": 1},
            {"question": "Bounce rate (çıkış oranı) yüksek olması ne anlama gelir?", "options": ["İyi bir şey", "Kullanıcıların sayfayı hızlı terk ettiği", "SEO başarısı", "Yüksek trafik"], "correct_index": 1},
            {"question": "Rich snippets nedir?", "options": ["HTML kod yapısı", "Arama sonuçlarında gelişmiş görünüm", "Backlink türü", "Meta tag"], "correct_index": 1},
            {"question": "Anchor text nedir?", "options": ["Sayfa başlığı", "Link verilen metin", "Meta açıklama", "H1 etiketi"], "correct_index": 1},
            {"question": "Duplicate content nedir?", "options": ["Aynı içeriğin farklı URL'lerde bulunması", "Orijinal içerik", "Kısa içerik", "Uzun içerik"], "correct_index": 0},
            {"question": "404 hatası SEO için ne anlama gelir?", "options": ["Sayfa bulunamadı - SEO için zararlı", "Sayfa başarıyla yüklendi", "Yönlendirme başarılı", "SEO için faydalı"], "correct_index": 0},
            {"question": "Robots.txt dosyası ne işe yarar?", "options": ["Arama motorlarına hangi sayfaları indekslememesi gerektiğini söyler", "Sayfa hızını artırır", "Backlink oluşturur", "Meta tag ekler"], "correct_index": 0}
        ])
        quiz1 = Quiz(title="SEO Bilgisi", lesson=l1_6, questions=quiz1_questions)

        quiz2_questions = json.dumps([
            {"question": "Flask'te bir route tanımlamak için hangi decorator kullanılır?", "options": ["@app.route()", "@flask.route()", "@route()", "@web.route()"], "correct_index": 0},
            {"question": "Jinja2'de değişken yazdırmak için hangi sözdizimi kullanılır?", "options": ["{% variable %}", "{{ variable }}", "{ variable }", "<?php echo $variable; ?>"], "correct_index": 1},
            {"question": "Flask'te template dosyaları hangi klasörde saklanır?", "options": ["static/", "templates/", "views/", "html/"], "correct_index": 1},
            {"question": "Flask-WTF ile form validasyonu için hangi kütüphane kullanılır?", "options": ["WTForms", "HTML Forms", "Django Forms", "Bootstrap Forms"], "correct_index": 0},
            {"question": "SQLAlchemy ORM'de bir model oluşturmak için hangi sınıf kullanılır?", "options": ["db.Model", "db.Table", "db.Database", "db.Schema"], "correct_index": 0},
            {"question": "Flask Blueprint nedir?", "options": ["Bir route", "Modüler uygulama yapısı", "Bir template", "Bir veritabanı"], "correct_index": 1},
            {"question": "Flask'te debug modu ne için kullanılır?", "options": ["Üretim için", "Geliştirme sırasında hata ayıklama", "Hız artırma", "Güvenlik"], "correct_index": 1},
            {"question": "Jinja2'de template kalıtımı için hangi komut kullanılır?", "options": ["{% include %}", "{% extends %}", "{% block %}", "{% import %}"], "correct_index": 1},
            {"question": "Flask'te static dosyalar hangi klasörde saklanır?", "options": ["static/", "assets/", "public/", "files/"], "correct_index": 0},
            {"question": "Flask-SQLAlchemy'de veritabanı işlemlerini kaydetmek için hangi metod kullanılır?", "options": ["db.save()", "db.commit()", "db.store()", "db.write()"], "correct_index": 1},
            {"question": "Jinja2'de döngü yapmak için hangi komut kullanılır?", "options": ["{% for %}", "{% loop %}", "{% while %}", "{% iterate %}"], "correct_index": 0},
            {"question": "Flask'te route'a parametre eklemek için nasıl yapılır?", "options": ["@app.route('/user/<id>')", "@app.route('/user/:id')", "@app.route('/user/{id}')", "@app.route('/user/$id')"], "correct_index": 0},
            {"question": "WTForms'da form alanını zorunlu yapmak için hangi validator kullanılır?", "options": ["Required()", "DataRequired()", "Mandatory()", "MustFill()"], "correct_index": 1},
            {"question": "SQLAlchemy'de One-to-Many ilişki tanımlamak için hangi metod kullanılır?", "options": ["db.relationship()", "db.link()", "db.connect()", "db.join()"], "correct_index": 0},
            {"question": "Flask'te request objesi hangi modülden import edilir?", "options": ["from flask import request", "from flask import Request", "import request", "from http import request"], "correct_index": 0},
            {"question": "Jinja2'de koşul kontrolü için hangi komut kullanılır?", "options": ["{% if %}", "{% check %}", "{% condition %}", "{% when %}"], "correct_index": 0},
            {"question": "Flask Blueprint oluşturmak için hangi sınıf kullanılır?", "options": ["Blueprint()", "FlaskBlueprint()", "Module()", "Component()"], "correct_index": 0},
            {"question": "SQLAlchemy'de sorgu yapmak için hangi metod kullanılır?", "options": [".query", ".search", ".find", ".select"], "correct_index": 0},
            {"question": "Flask'te flash mesajı göstermek için hangi fonksiyon kullanılır?", "options": ["flash()", "message()", "alert()", "notify()"], "correct_index": 0},
            {"question": "Jinja2'de filtre uygulamak için hangi sembol kullanılır?", "options": ["|", ":", ">", "<"], "correct_index": 0}
        ])
        quiz2 = Quiz(title="Flask ve Web Geliştirme Bilgisi", lesson=l2_8, questions=quiz2_questions)
        
        # Quiz 3 - Sosyal Medya Yönetimi için
        quiz3_questions = json.dumps([
            {"question": "Hangi sosyal medya platformu B2B pazarlama için en uygundur?", "options": ["Facebook", "LinkedIn", "TikTok", "Snapchat"], "correct_index": 1},
            {"question": "Sosyal medya içerik planlamasında en önemli faktör nedir?", "options": ["Sık paylaşım", "Tutarlılık ve kalite", "Sadece görsel", "Sadece metin"], "correct_index": 1},
            {"question": "Instagram Stories için ideal içerik süresi nedir?", "options": ["30 saniye", "15 saniye", "60 saniye", "5 dakika"], "correct_index": 1},
            {"question": "Sosyal medya reklamlarında CTR ne anlama gelir?", "options": ["Cost per click", "Click-through rate", "Conversion rate", "Return on investment"], "correct_index": 1},
            {"question": "Hashtag stratejisinde hangisi doğrudur?", "options": ["Çok fazla hashtag kullanmak", "Hedef kitleye uygun, orta sayıda hashtag", "Hiç hashtag kullanmamak", "Sadece marka hashtag'i"], "correct_index": 1},
            {"question": "Facebook Ads'de hangi hedefleme seçeneği yoktur?", "options": ["Demografik", "İlgi alanları", "Telefon numarası", "Davranışsal"], "correct_index": 2},
            {"question": "Sosyal medya içeriklerinde en yüksek etkileşim hangi saatlerde alınır?", "options": ["Sabah 6-8", "Öğle 12-14", "Akşam 18-21", "Gece 23-01"], "correct_index": 2},
            {"question": "Instagram'da algoritma için en önemli faktör nedir?", "options": ["Takipçi sayısı", "Etkileşim oranı", "Paylaşım sıklığı", "Hesap yaşı"], "correct_index": 1},
            {"question": "LinkedIn'de profesyonel içerik paylaşımı için ideal format nedir?", "options": ["Sadece görsel", "Uzun metin + görsel", "Sadece video", "Sadece link"], "correct_index": 1},
            {"question": "Sosyal medya krizi yönetiminde ilk adım nedir?", "options": ["Hemen yanıt vermek", "Durumu analiz etmek", "Hesabı kapatmak", "Yorumları silmek"], "correct_index": 1},
            {"question": "Twitter'da karakter limiti nedir?", "options": ["140", "280", "500", "Sınırsız"], "correct_index": 1},
            {"question": "Sosyal medya ROI ölçümünde hangi metrik kullanılmaz?", "options": ["Etkileşim sayısı", "Dönüşüm oranı", "Takipçi sayısı", "İçerik kalitesi"], "correct_index": 3},
            {"question": "Instagram Reels'in maksimum süresi nedir?", "options": ["15 saniye", "30 saniye", "60 saniye", "90 saniye"], "correct_index": 3},
            {"question": "Facebook'ta en iyi görsel boyutu nedir?", "options": ["1200x630 px", "800x600 px", "1920x1080 px", "500x500 px"], "correct_index": 0},
            {"question": "Sosyal medya içerik takvimi oluştururken hangisi önemlidir?", "options": ["Sadece tarihler", "İçerik türleri, tarihler ve saatler", "Sadece platformlar", "Sadece hashtag'ler"], "correct_index": 1},
            {"question": "LinkedIn'de en etkili içerik türü nedir?", "options": ["Eğlenceli meme'ler", "Profesyonel makaleler ve endüstri içgörüleri", "Kişisel fotoğraflar", "Sadece link paylaşımları"], "correct_index": 1},
            {"question": "Sosyal medya algoritması için 'engagement rate' ne anlama gelir?", "options": ["Takipçi sayısı", "Etkileşim oranı (beğeni, yorum, paylaşım)", "Görüntülenme sayısı", "Tıklama sayısı"], "correct_index": 1},
            {"question": "Instagram'da hashtag araştırması için hangi araç kullanılabilir?", "options": ["Sadece Instagram", "Hashtagify, RiteTag", "Sadece Google", "Sadece Facebook"], "correct_index": 1},
            {"question": "Sosyal medya içerik stratejisinde 'content pillar' nedir?", "options": ["Sosyal medya direği", "İçerik temaları/kategorileri", "Paylaşım zamanı", "Hashtag stratejisi"], "correct_index": 1},
            {"question": "Twitter'da 'thread' nedir?", "options": ["Tek bir tweet", "Birbirine bağlı birden fazla tweet", "Retweet", "Yorum"], "correct_index": 1}
        ])
        quiz3 = Quiz(title="Sosyal Medya Yönetimi Bilgisi", lesson=l3_4, questions=quiz3_questions)
        
        # Dersler (Course 4) - Kablosuz Ağlar
        l4_1_content = """<h3>📜 Bilgisayar Ağlarına Giriş ve Tarihçe</h3>
        <p>Bu bölüm, neden bilgisayar ağlarına ihtiyaç duyduğumuzu, ağların amacını ve her şeyin nasıl başladığını anlatıyor.</p>
        
        <h4>🤔 Bilgisayar Ağları Nedir ve Neden Önemlidir?</h4>
        <p><strong>Tanım:</strong> Bilgisayar ağları, en basit tanımıyla, bilgisayar sistemlerinin birbirine bağlanarak bilginin iletildiği ve paylaşıldığı yapılardır.</p>
        <p><strong>Bağlantı:</strong> İki bilgisayar bilgi alışverişinde bulunabiliyorsa, birbirine bağlıdır. Bu bağlantı sadece bakır tellerle olmaz; fiber optik kablolar, mikrodalgalar ve iletişim uyduları da kullanılabilir.</p>
        <p><strong>Geçmiş:</strong> Eskiden bilgisayarlar devasa, merkezi yapılardı ve sadece üniversiteler gibi büyük kurumlarda bulunurdu.</p>
        <p><strong>Günümüz:</strong> Bilgisayarlar küçüldükçe, bu "merkezi yapıdan" herkesin erişebildiği "dağıtık yapıya" geçildi.</p>
        <p><strong>Önemli Not:</strong> 21. Yüzyıl "Bilgi Çağı" olarak adlandırılmaktadır. Bilgi çok hızlı üretilir ve değişir. Dünyadaki gelişmeleri takip etmek için bilgilerin paylaşılarak çoğaltılması gerekir ve ağlar bunu sağlar.</p>
        
        <h4>🎯 Bilgisayar Ağlarının Amaçları Nelerdir?</h4>
        <p>Ağlar şu amaçlar için kurulur:</p>
        <ul>
            <li>📁 <strong>Veri Paylaşımı</strong></li>
            <li>💬 <strong>Haberleşme</strong></li>
            <li>🖨 <strong>Bilgisayar Kaynaklarının Paylaşımı</strong> (Yazıcı, donanım vb.)</li>
            <li>💻 <strong>Yazılımların Paylaşımı</strong></li>
            <li>🔐 <strong>Yüksek Güvenilirlik:</strong> Önemli bir dosya birkaç kaynakta birden tutulabilir; birinde sorun çıkarsa diğerleri kullanılır.</li>
            <li>🚀 <strong>Yüksek İşlem hızının Sağlanması</strong></li>
            <li>🏢 <strong>Merkezi Yönetim</strong></li>
            <li>🤝 <strong>Ortak Çalışma Grupları:</strong> Uzaktaki iki veya daha fazla kişi ortak bir raporu beraber yazabilir.</li>
        </ul>
        
        <h4>⏳ Ağların Tarihsel Gelişimi (İnternet'in Doğuşu)</h4>
        <ul>
            <li><strong>1969:</strong> ABD'de, savunma amacıyla ARPANET adında bir bilgisayar ağı hazırlandı. Strateji uzmanları bu ağı fikir alışverişi için kullanıyordu.</li>
            <li><strong>1972:</strong> ARPANET, bir konferans aracılığıyla kamuoyuna tanıtıldı.</li>
            <li><strong>1980:</strong> Farklı ağların birbirleriyle irtibat kurmasına izin veren protokol imzalandı.</li>
            <li><strong>1983:</strong> ARPANET, askeri ve sivil olarak iki ağa ayrıldığında, ortaya çıkan bu ferdi ağların bütününü ifade etmek için İnternet ismi teklif edildi.</li>
        </ul>
        <p><strong>İnternet Nedir?</strong> Değişik özelliklerdeki küçük ağların (Ethernet, Token Ring vb.) birbirine bağlanmasıyla oluşan ve tek bir ağ gibi davranan en büyük ağdır.</p>"""
        
        l4_2_content = """<h3>📡 Kablosuz İletişimin Temelleri</h3>
        <p>Kablosuz iletişim, "tel" kullanmadan RF (Radyo Frekansı) teknolojisi ile hava üzerinden bilgi alışverişi yapan sistemdir.</p>
        
        <h4>🔑 Temel Terimler</h4>
        <ul>
            <li><strong>SSID:</strong> Kablosuz ağın adıdır (Wi-Fi ağ adı).</li>
            <li><strong>WLAN:</strong> Kablosuz Yerel Alan Ağı (Wi-Fi gibi).</li>
            <li><strong>AP (Access Point):</strong> Kablosuz erişim noktası, cihazları birbirine bağlayan veya internete çıkış sağlayan cihaz.</li>
            <li><strong>Modülasyon:</strong> Bilgi sinyalini uzak mesafelere gidebilmesi için taşıyıcı sinyale bindirme işlemi.</li>
            <li><strong>RF (Radyo Frekansı):</strong> Duvar gibi engellerden geçebilen elektromanyetik dalgalar.</li>
        </ul>
        
        <h4>🌐 Kablosuz İletişim Türleri</h4>
        <ul>
            <li><strong>Radyo Dalgaları:</strong> Her yöne yayın yapabilen dalgalar (Wi-Fi, Bluetooth).</li>
            <li><strong>Mikrodalga:</strong> Tek yönlü, odaklı yayın (uydu sistemleri).</li>
            <li><strong>Kızılötesi (IR):</strong> Kısa menzilli (10-15m), cihazların birbirini görmesi gerekir.</li>
        </ul>"""
        
        l4_3_content = """<h3>💻 Kablosuz Ağ Teknolojileri</h3>
        
        <h4>🔵 Bluetooth</h4>
        <ul>
            <li>Kısa mesafeli (10-100m) ses ve veri iletimi.</li>
            <li>2.4 GHz frekans bandı, 24 Mbps hız.</li>
            <li>Kablosuz kulaklık, fare, klavye gibi cihazlarda kullanılır.</li>
        </ul>
        
        <h4>📶 Wi-Fi (WLAN)</h4>
        <p>Kablosuz Yerel Alan Ağı - Ev ve iş yerlerinde kullanılan en yaygın kablosuz teknolojidir.</p>
        <ul>
            <li><strong>Avantajlar:</strong> Hareketlilik, düşük maliyet, hızlı kurulum, ölçeklenebilirlik.</li>
            <li><strong>Dezavantajlar:</strong> Girişim riski, güvenlik açığı (şifreleme şart!).</li>
        </ul>
        
        <h4>🌐 WiMAX</h4>
        <p>Wi-Fi'nin geniş alan versiyonu - 50 km'ye kadar kapsama alanı.</p>
        
        <h4>📊 Ağ Sınıflandırması (Menzil)</h4>
        <ul>
            <li><strong>WPAN:</strong> Kişisel alan (Bluetooth, IR) - 1-10m</li>
            <li><strong>WLAN:</strong> Yerel alan (Wi-Fi) - Bina/kampüs</li>
            <li><strong>WMAN:</strong> Metropol alan (WiMAX) - Şehir</li>
            <li><strong>WWAN:</strong> Geniş alan (GSM, 3G/4G/5G) - Ülke/kıta</li>
        </ul>"""
        
        l4_4_content = """<h3>📡 Sayısal İletişimin Temelleri</h3>
        <p>Bilgi üç yolla iletilebilir: Kablo, optik fiber veya hava (elektromanyetik dalgalar).</p>
        
        <h4>⚡ Analog vs Sayısal</h4>
        <ul>
            <li><strong>Analog:</strong> Sürekli değerler (örnek: ses dalgası, eski telefon).</li>
            <li><strong>Sayısal:</strong> Kesikli değerler (0 ve 1'ler, modern sistemler).</li>
        </ul>
        
        <h4>🔄 Dönüşüm</h4>
        <ul>
            <li><strong>ADC:</strong> Analog → Sayısal (gönderici tarafında).</li>
            <li><strong>DAC:</strong> Sayısal → Analog (alıcı tarafında, örn: hoparlör).</li>
        </ul>"""
        
        l4_5_content = """<h3>🚀 Haberleşme Sisteminin Yapısı</h3>
        <p>Bir haberleşme sisteminde 3 ana bileşen vardır:</p>
        <ol>
            <li><strong>Verici:</strong> Bilgiyi gönderir (kodlama, modülasyon).</li>
            <li><strong>Kanal:</strong> İletim ortamı (kablo, fiber veya hava).</li>
            <li><strong>Alıcı:</strong> Bilgiyi alır (demodülasyon, kod çözme).</li>
        </ol>
        
        <h4>✨ Sayısal Haberleşmenin Avantajları</h4>
        <ul>
            <li>Gürültüye dayanıklı, hata kontrolü yapılabilir.</li>
            <li>Uzun mesafe iletimi kolay, depolama ucuz.</li>
            <li>🚨 <strong>Şifreleme mümkün</strong> - Güvenlik için kritik!</li>
        </ul>
        
        <h4>👎 Dezavantajları</h4>
        <ul>
            <li>Daha fazla bant genişliği gerektirir.</li>
            <li>Senkronizasyon (zamanlama) gerektirir.</li>
        </ul>"""
        
        l4_6_content = """<h3>📊 Veri İletimi Karakteristikleri</h3>
        <p>Veri, 0 ve 1'ler (bitler) şeklinde ikilik tabanda iletilir. Yüksek seviye "1", alçak seviye "0" anlamına gelir.</p>
        
        <h4>🔑 Temel Terimler</h4>
        <ul>
            <li><strong>Bit/sn (bit/s):</strong> Saniyede iletilen bit sayısı (hız).</li>
            <li><strong>Band Genişliği:</strong> Bir hattın taşıyabildiği frekans aralığı.</li>
            <li><strong>Modülasyon:</strong> Veriyi iletim ortamına uygun hale getirme işlemi.</li>
        </ul>
        <p><strong>Örnek:</strong> 2400 bit/sn hızında 8 bitlik kodlar kullanılırsa, saniyede 300 karakter (2400÷8) iletilebilir.</p>"""
        
        l4_7_content = """<h3>📥 Veri İletiminin Temelleri</h3>
        <p>Veri iletimi, bilginin bir noktadan diğerine aktarılmasıdır. Günümüzde hem kablolu hem kablosuz olarak yüksek hızlarda yapılır.</p>
        
        <h4>📦 Veri İletim Sisteminin 5 Elemanı</h4>
        <ol>
            <li><strong>Gönderici:</strong> Veriyi ileten cihaz (PC, sunucu).</li>
            <li><strong>Alıcı:</strong> Veriyi alan cihaz (PC, sunucu, TV).</li>
            <li><strong>Mesaj:</strong> İletilen veri (ses, görüntü, metin).</li>
            <li><strong>İletim Ortamı:</strong> Fiziksel yol (kablo, fiber, radyo dalgaları).</li>
            <li><strong>Protokol:</strong> İletişimi yöneten kurallar.</li>
        </ol>"""
        
        l4_8_content = """<h3>🚦 Veri İletim Yöntemleri</h3>
        
        <h4>1. Paralel İletim</h4>
        <ul>
            <li>8 bit aynı anda 8 ayrı hat üzerinden gönderilir.</li>
            <li>Çok hızlı, ancak kısa mesafeler için (CPU-RAM arası).</li>
        </ul>
        
        <h4>2. Seri İletim</h4>
        <ul>
            <li>Bitler tek hat üzerinden sırayla gönderilir.</li>
            <li>Daha yavaş ama uzun mesafeler için verimli ve ucuz (ağlar için ideal).</li>
        </ul>"""
        
        l4_9_content = """<h3>⏰ Seri İletim Tipleri</h3>
        
        <h4>1. Asenkron (Eşzamansız)</h4>
        <ul>
            <li>Her veri paketinin başına Start biti, sonuna Stop biti eklenir.</li>
            <li>Veri birimleri arasında boşluklar olur, daha yavaş.</li>
            <li>Basit ve ucuz sistemler için uygundur.</li>
        </ul>
        
        <h4>2. Senkron (Eşzamanlı)</h4>
        <ul>
            <li>Start/Stop bitleri yok, sürekli ve hızlı iletişim.</li>
            <li>Gönderici ve alıcı "saat bilgisi" ile eşzamanlı çalışır.</li>
            <li>Daha hızlı ve verimli.</li>
        </ul>"""
        
        l4_10_content = """<h3>↔ Veri İletişim Yönleri</h3>
        
        <ul>
            <li><strong>Simplex:</strong> Tek yönlü (TV/radyo yayınları, TV kumandası).</li>
            <li><strong>Half-Duplex:</strong> Çift yönlü ama aynı anda değil (telsizler - Bas-Konuş).</li>
            <li><strong>Full-Duplex:</strong> Aynı anda çift yönlü (telefon, internet bağlantısı).</li>
        </ul>"""
        
        l4_11_content = """<h3>📡 İletim Tipleri</h3>
        
        <ul>
            <li><strong>Baseband:</strong> Aynı anda tek sinyal (Ethernet ağları).</li>
            <li><strong>Broadband:</strong> Farklı frekanslarla aynı anda birden fazla sinyal (TV yayınları - tek kablodan yüzlerce kanal).</li>
        </ul>"""
        
        l4_12_content = """<h3>🛣 Veri İletim Ortamları</h3>
        
        <h4>1. Kablolu (Kılavuzlu)</h4>
        <ul>
            <li><strong>Bükümlü Çift:</strong> En yaygın (telefon, internet).</li>
            <li><strong>Koaksiyel:</strong> TV ağları, geniş bant internet.</li>
            <li><strong>Optik Fiber:</strong> Işık ile veri iletimi, çok yüksek hız.</li>
        </ul>
        
        <h4>2. Kablosuz (Kılavuzsuz)</h4>
        <ul>
            <li><strong>Radyo Dalgaları:</strong> En yaygın, duvarlardan geçebilir (Wi-Fi, mobil).</li>
            <li><strong>Mikrodalga:</strong> Yüksek frekans, net görüş hattı gerekir (uydu, mobil).</li>
            <li><strong>Kızılötesi (IR):</strong> Kısa menzil, duvarlardan geçemez (uzaktan kumanda).</li>
        </ul>"""
        
        l4_13_content = """<h3>📋 Ortam Seçimini Etkileyen Faktörler</h3>
        <p>Bir ağ kurarken hangi ortamı seçmek için şu faktörlere bakılır:</p>
        <ul>
            <li>İletim hızı</li>
            <li>Kurulum maliyeti ve kolaylığı</li>
            <li>Çevre koşullarına dayanıklılık</li>
            <li>Mesafe</li>
            <li>🚨 <strong>Ağ güvenliği</strong> (kritik!)</li>
        </ul>
        <p>Doğru ortam seçimi, ağın verimliliği ve güvenliği için kritik öneme sahiptir.</p>"""
        
        l4_1 = Lesson(course=course4, order=1, title="Bilgisayar Ağlarına Giriş ve Tarihçe", lesson_type="Metin", content=l4_1_content)
        l4_2 = Lesson(course=course4, order=2, title="Kablosuz İletişimin Temelleri ve Kavramları", lesson_type="Metin", content=l4_2_content)
        l4_3 = Lesson(course=course4, order=3, title="Kablosuz Ağ Teknolojileri ve Standartları", lesson_type="Metin", content=l4_3_content)
        l4_4 = Lesson(course=course4, order=4, title="Sayısal İletişimin Temelleri", lesson_type="Metin", content=l4_4_content)
        l4_5 = Lesson(course=course4, order=5, title="Haberleşme Sisteminin Yapısı ve Veri İletimi", lesson_type="Metin", content=l4_5_content)
        l4_6 = Lesson(course=course4, order=6, title="Veri İletimi Karakteristikleri", lesson_type="Metin", content=l4_6_content)
        l4_7 = Lesson(course=course4, order=7, title="Veri İletiminin Temelleri", lesson_type="Metin", content=l4_7_content)
        l4_8 = Lesson(course=course4, order=8, title="Veri İletim Yöntemleri (Seri vs. Paralel)", lesson_type="Metin", content=l4_8_content)
        l4_9 = Lesson(course=course4, order=9, title="Seri İletim Tipleri (Asenkron vs. Senkron)", lesson_type="Metin", content=l4_9_content)
        l4_10 = Lesson(course=course4, order=10, title="Veri İletişim Yönleri", lesson_type="Metin", content=l4_10_content)
        l4_11 = Lesson(course=course4, order=11, title="İletim Tipleri (Baseband vs. Broadband)", lesson_type="Metin", content=l4_11_content)
        l4_12 = Lesson(course=course4, order=12, title="Veri İletim Ortamları (Kablolu vs. Kablosuz)", lesson_type="Metin", content=l4_12_content)
        l4_13 = Lesson(course=course4, order=13, title="Ortam Seçimini Etkileyen Faktörler", lesson_type="Metin", content=l4_13_content)
        l4_14 = Lesson(course=course4, order=14, title="Quiz: Kablosuz Ağlar Bilgisi", lesson_type="Quiz", content="Kablosuz ağlar konularındaki bilginizi test edin.")
        
        db.session.add_all([l4_1, l4_2, l4_3, l4_4, l4_5, l4_6, l4_7, l4_8, l4_9, l4_10, l4_11, l4_12, l4_13, l4_14])
        db.session.commit()
        
        # Quiz 4 - Kablosuz Ağlar için 20 soru
        quiz4_questions = json.dumps([
            {"question": "Kablosuz iletişim nedir?", "options": ["Tel kullanarak yapılan iletişim", "Tel kullanmadan yapılan iletişim", "Sadece radyo ile iletişim", "Sadece internet iletişimi"], "correct_index": 1},
            {"question": "Bluetooth hangi frekans bandında çalışır?", "options": ["5 GHz", "2.4 GHz", "900 MHz", "1.8 GHz"], "correct_index": 1},
            {"question": "WLAN'ın açılımı nedir?", "options": ["Wireless Local Area Network", "Wide Local Area Network", "Wireless Long Area Network", "Wired Local Area Network"], "correct_index": 0},
            {"question": "SSID ne anlama gelir?", "options": ["Service Set Identifier", "System Security ID", "Signal Strength ID", "Server Service ID"], "correct_index": 0},
            {"question": "WiMAX'in menzili yaklaşık ne kadar olabilir?", "options": ["10 km", "50 km", "100 km", "5 km"], "correct_index": 1},
            {"question": "Kızılötesi (IR) iletişimin menzili yaklaşık ne kadardır?", "options": ["100-200 m", "10-15 m", "1-2 km", "50-100 m"], "correct_index": 1},
            {"question": "ARPANET hangi yılda kuruldu?", "options": ["1972", "1969", "1983", "1980"], "correct_index": 1},
            {"question": "Analog sinyalin özelliği nedir?", "options": ["Kesikli değerler alır", "Sürekli değerler alır", "Sadece 0 ve 1 değerleri", "Sadece dijital"], "correct_index": 1},
            {"question": "Sayısal sinyalin özelliği nedir?", "options": ["Sürekli değerler alır", "Kesikli değerler alır", "Analog sinyale benzer", "Her zaman süreklidir"], "correct_index": 1},
            {"question": "ADC ne işe yarar?", "options": ["Analog sinyali sayısala çevirir", "Sayısal sinyali analoga çevirir", "Sinyali güçlendirir", "Sinyali filtreler"], "correct_index": 0},
            {"question": "DAC ne işe yarar?", "options": ["Analog sinyali sayısala çevirir", "Sayısal sinyali analoga çevirir", "Sinyali güçlendirir", "Sinyali filtreler"], "correct_index": 1},
            {"question": "Simplex iletişim nedir?", "options": ["Çift yönlü iletişim", "Tek yönlü iletişim", "Aynı anda çift yönlü", "Yarım çift yönlü"], "correct_index": 1},
            {"question": "Full-Duplex iletişim nedir?", "options": ["Tek yönlü iletişim", "Aynı anda çift yönlü iletişim", "Yarım çift yönlü", "Sadece alıcı"], "correct_index": 1},
            {"question": "Paralel iletimde kaç hat kullanılır (8 bit için)?", "options": ["1 hat", "4 hat", "8 hat", "16 hat"], "correct_index": 2},
            {"question": "Seri iletimde kaç hat kullanılır?", "options": ["8 hat", "1 hat", "4 hat", "16 hat"], "correct_index": 1},
            {"question": "Asenkron iletişimde hangi bitler eklenir?", "options": ["Sadece Start biti", "Start ve Stop bitleri", "Sadece Stop biti", "Hiç bit eklenmez"], "correct_index": 1},
            {"question": "Baseband iletişimde ne olur?", "options": ["Aynı anda birden fazla sinyal", "Aynı anda sadece tek sinyal", "Sinyal gönderilmez", "Sadece analog sinyal"], "correct_index": 1},
            {"question": "Broadband iletişimde ne olur?", "options": ["Aynı anda sadece tek sinyal", "Aynı anda birden fazla sinyal (farklı frekanslar)", "Sinyal gönderilmez", "Sadece dijital sinyal"], "correct_index": 1},
            {"question": "Optik fiber kablo veriyi nasıl iletir?", "options": ["Elektrik akımı ile", "Işık darbeleri ile", "Radyo dalgaları ile", "Mikrodalga ile"], "correct_index": 1},
            {"question": "Ağ güvenliği için en kritik faktör nedir?", "options": ["Hız", "Şifreleme ve Yetkilendirme", "Menzil", "Frekans"], "correct_index": 1}
        ])
        quiz4 = Quiz(title="Kablosuz Ağlar Bilgisi", lesson=l4_14, questions=quiz4_questions)
        
        db.session.add_all([quiz1, quiz2, quiz3, quiz4])
        db.session.commit()
        current_app.logger.info("Kurslar, dersler ve quizler başarıyla eklendi.")


        current_app.logger.info("8/9: Personel kurs kayıtları ve ilerlemeleri simüle ediliyor...")
        enrollments = []
        for person in active_personnel:
            # Her personeli rastgele 1-2 kursa kaydet
            for course in random.sample([course1, course2, course3, course4], k=random.randint(1, 2)):
                if person.id and course.id: # ID'lerin olduğundan emin ol
                    enrollment = Enrollment(student=person, course=course)
                    enrollments.append(enrollment)
                    db.session.add(enrollment)
        try:
            db.session.flush() # Kayıt ID'lerini al
            # Kayıtlı derslere rastgele ilerleme ekle
            for enrollment in enrollments:
                course_lessons = enrollment.course.lessons.all()
                if course_lessons:
                    # Rastgele sayıda dersi tamamla (0 ile hepsi arası)
                    num_to_complete = random.randint(0, len(course_lessons))
                    lessons_to_complete = random.sample(course_lessons, k=num_to_complete)
                    for lesson in lessons_to_complete:
                        enrollment.add_completed_lesson(lesson.id) # Modeldaki metodu kullan
            db.session.commit()
            current_app.logger.info("Kurs kayıtları ve ilerlemeler başarıyla eklendi.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Kurs kayıtları/ilerlemeler eklenirken hata: {e}", exc_info=True)


        current_app.logger.info("9/9: Çeşitli aktivite kayıtları (log) oluşturuluyor...")
        # Aktif personellerden ve admin'den rastgele seç
        log_users = random.sample(active_personnel + [admin_user], k=min(10, len(active_personnel) + 1))
        log_actions = [
            ("sisteme giriş yaptı.", None, None),
            (f"<strong>{random.choice(projects_list).title}</strong> projesini güncelledi.", 'Project', random.choice(projects_list).id),
            (f"<strong>{random.choice(packages_list).name}</strong> paketini sildi.", 'Package', random.choice(packages_list).id),
            (f"'{random.choice([course1, course2, course3, course4]).title}' kursuna yeni bir ders ekledi.", 'Course', random.choice([course1, course2, course3, course4]).id),
            ("profil bilgilerini güncelledi.", 'User', lambda u: u.id), # Lambda ile user ID'yi al
            (f"'{random.choice([l1_2, l2_2, l3_1]).title}' dersini tamamladı.", 'Lesson', random.choice([l1_2, l2_2, l3_1]).id)
        ]

        for i in range(15): # 15 rastgele log oluştur
            user = random.choice(log_users)
            action_data = random.choice(log_actions)
            action_text = action_data[0]
            target_type = action_data[1]
            target_id_val = action_data[2]
            target_id = target_id_val(user) if callable(target_id_val) else target_id_val

            # Kullanıcı ID'sinin olduğundan emin ol
            if user.id is None:
                 db.session.flush([user])
                 if user.id is None: continue # Hala ID yoksa atla

            log_entry = ActivityLog(
                user_id=user.id,
                action=action_text,
                target_type=target_type,
                target_id=target_id,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            )
            db.session.add(log_entry)

        try:
            db.session.commit()
            current_app.logger.info("Aktivite logları başarıyla eklendi.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Aktivite logları eklenirken hata: {e}", exc_info=True)


        current_app.logger.info("--- Veritabanı Tohumlama Başarıyla Tamamlandı! ---")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"!!! TOHUMLAMA SIRASINDA KRİTİK HATA: İşlem geri alındı !!!", exc_info=True)
        print(f"\n!!! BİR HATA OLUŞTU: Tohumlama işlemi geri alındı. Logları kontrol edin. !!!")
        print(f"Hata Detayı: {e}")

    finally:
        current_app.logger.info("--- Tohumlama script'i çalışmasını tamamladı. ---")