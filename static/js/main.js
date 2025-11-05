/**
 * ===================================================================
 * KUWAMEDYA - PROJE ANA SCRİPT DOSYASI (main.js)
 * Sürüm: v5.0 (Kusursuz & Ultra Donanımlı)
 *
 * BU DOSYA, KUWAMEDYA PROJESİNİN TÜM İNTERAKTİF İŞLEVSELLİĞİNİ
 * PROFESYONEL BİR YAPI (NESNE YÖNELİMLİ) İÇİNDE YÖNETİR.
 *
 * MİMARİ:
 * KuwamedyaApp
 * ├── Core      (Site geneli: preloader, scroll-top, AOS)
 * ├── Vitrin    (Vitrin sayfaları: sayaçlar, portfolyo filtresi)
 * ├── Auth      (Login/Register: şifre gücü, şifre gösterme)
 * ├── Panel     (Admin/Personel: grafikler, anlık arama, modallar)
 * └── Academy   (LMS: dinamik kurs listesi, oyunlaştırılmış sınav motoru)
 *
 * "TOP SEVİYE" GÜNCELLEMELERİ:
 * 1.  TAMAMEN MODÜLER: Tüm mantık, `KuwamedyaApp` adında tek bir
 * nesne içinde kapsüllenmiştir. `init()` fonksiyonu, DOM
 * yüklendiğinde ilgili modülleri başlatır.
 * 2.  TEMİZLİK (DRY PRENSİBİ): Bu merkezi dosya sayesinde, `register.html`,
 * `quiz.html`, `list_users.html` gibi şablonların içindeki
 * TÜM `<script>` bloklarını kaldırdık. Artık tüm JS mantığı
 * tek bir yerde!
 * 3.  HATAYA DAYANIKLI: Her modül, sadece ilgili HTML elementleri
 * (örn: `document.getElementById('quiz-card')`) sayfada
 * bulunursa çalışır. Bu, konsol hatalarını engeller.
 * ===================================================================
 */

const KuwamedyaApp = {

    /**
     * UYGULAMA BAŞLATMA
     * Sayfa yüklendiğinde tüm modülleri sırayla başlatır.
     */
    init() {
        // DOM (HTML) tamamen yüklendiğinde fonksiyonları çalıştır
        document.addEventListener('DOMContentLoaded', () => {
            console.log('KuwamedyaApp v5.0 Başlatılıyor...');
            
            // Çekirdek (Core) modülü her zaman çalışır
            this.Core.init();
            
            // Sadece ilgili sayfalarda çalışacak modülleri başlat
            this.Vitrin.init();
            this.Auth.init();
            this.Panel.init();
            this.Academy.init();
            
            console.log('KuwamedyaApp v5.0 Başarıyla Yüklendi.');
        });
    },

    /**
     * ===================================================================
     * BÖLÜM 1: ÇEKİRDEK MODÜLÜ (CORE)
     * Site genelinde çalışan temel fonksiyonlar.
     * `layout.html`'deki elementleri (Preloader, ScrollTop) yönetir.
     * ===================================================================
     */
    Core: {
        init() {
            // Bu fonksiyonlar her sayfada çalışmayı deneyecek
            this.initPreloader();
            this.initScrollTopButton();
            this.initDynamicYear();
            this.initAOS();
            this.initBootstrapTooltips();
            this.initThemeToggle();
            this.initScrollReveal();
            this.initHoverEffects();
            console.log('Çekirdek Modülü Yüklendi.');
        },

        // 'layout.html'deki #preloader elementini yönetir
        initPreloader() {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                window.addEventListener('load', () => {
                    preloader.classList.add('fade-out');
                    // Animasyon bittikten sonra DOM'dan kaldır
                    setTimeout(() => preloader.remove(), 500); 
                });
            }
        },

        // 'layout.html'deki .scroll-top-btn elementini yönetir
        initScrollTopButton() {
            const scrollTopBtn = document.querySelector('.scroll-top-btn');
            if (scrollTopBtn) {
                window.addEventListener('scroll', () => {
                    if (window.scrollY > 300) {
                        scrollTopBtn.classList.add('visible');
                    } else {
                        scrollTopBtn.classList.remove('visible');
                    }
                });
                scrollTopBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }
        },

        // 'layout.html' footer'ındaki #current-year span'ini doldurur
        initDynamicYear() {
            const yearSpan = document.getElementById('current-year');
            if (yearSpan) {
                yearSpan.textContent = new Date().getFullYear();
            }
        },

        // AOS (Animate on Scroll) kütüphanesini başlatır
        initAOS() {
            if (typeof AOS !== 'undefined') {
                AOS.init({
                    duration: 800,
                    easing: 'ease-in-out-cubic',
                    once: true,
                    offset: 50,
                });
            } else {
                console.warn('AOS kütüphanesi yüklenemedi.');
            }
        },

        // Bootstrap'in "tooltip" (ipucu) özelliğini tüm sayfada etkinleştirir
        initBootstrapTooltips() {
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
        },

        // Dark/Light mode toggle - Sadece butona basıldığında değişir, scroll ile tetiklenmez
        initThemeToggle() {
            const themeToggle = document.getElementById('theme-toggle');
            const themeIcon = document.getElementById('theme-icon');
            const body = document.getElementById('main-body');
            
            if (!themeToggle || !body) return;
            
            // LocalStorage'dan tema tercihini yükle (varsayılan: light)
            const savedTheme = localStorage.getItem('theme') || 'light';
            if (savedTheme === 'light') {
                body.setAttribute('data-bs-theme', 'light');
                body.classList.add('light-theme');
                if (themeIcon) {
                    themeIcon.classList.remove('fa-moon');
                    themeIcon.classList.add('fa-sun');
                }
            } else {
                // Dark tema için
                body.setAttribute('data-bs-theme', 'dark');
                body.classList.remove('light-theme');
                if (themeIcon) {
                    themeIcon.classList.remove('fa-sun');
                    themeIcon.classList.add('fa-moon');
                }
            }
            
            // Sadece butona tıklandığında tema değişir
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const currentTheme = body.getAttribute('data-bs-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                // Smooth geçiş animasyonu
                body.style.transition = 'background-color 0.4s ease, color 0.4s ease';
                
                body.setAttribute('data-bs-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // İkon animasyonu
                if (themeIcon) {
                    themeIcon.style.transform = 'rotate(360deg)';
                    themeIcon.style.transition = 'transform 0.5s ease';
                }
                
                if (newTheme === 'light') {
                    body.classList.add('light-theme');
                    if (themeIcon) {
                        themeIcon.classList.remove('fa-moon');
                        themeIcon.classList.add('fa-sun');
                    }
                } else {
                    body.classList.remove('light-theme');
                    if (themeIcon) {
                        themeIcon.classList.remove('fa-sun');
                        themeIcon.classList.add('fa-moon');
                    }
                }
                
                // İkon rotasyonunu sıfırla
                setTimeout(() => {
                    if (themeIcon) {
                        themeIcon.style.transform = 'rotate(0deg)';
                    }
                }, 500);
            });
            
            // Scroll event listener'larını kaldır - sadece buton ile değişir
        },

        // Scroll animasyonları için smooth reveal
        initScrollReveal() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, observerOptions);

            // Fade-in animasyonu için elementleri seç
            document.querySelectorAll('.fade-in-on-scroll').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        },

        // Hover efektleri için gelişmiş animasyonlar
        initHoverEffects() {
            // Kart hover efektleri
            document.querySelectorAll('.card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                    this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
                    this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.15)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '';
                });
            });

            // Buton ripple efekti
            document.querySelectorAll('.btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';
                    ripple.classList.add('ripple');
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => ripple.remove(), 600);
                });
            });
        }
    }, // <-- BÖLÜM 1 SONU (Core Modülü bitti)

    /**
     * ===================================================================
     * BÖLÜM 2: VİTRİN MODÜLÜ
     * index.html, packages.html, portfolio.html sayfalarını yönetir.
     * ===================================================================
     */
    Vitrin: {
        init() {
            // Bu modülün fonksiyonları sadece ilgili elementler varsa çalışır
            if (document.querySelector('.counter')) {
                this.initStatCounters();
            }
            if (document.getElementById('pricing-toggle-switch')) {
                this.initPricingToggle();
            }
            // Isotope ve imagesLoaded kütüphaneleri layout.html'de yüklü olmalı
            // (veya portfolio.html'nin block scripts'inde)
            if (document.querySelector('.portfolio-container') && typeof Isotope !== 'undefined' && typeof imagesLoaded !== 'undefined') {
                this.initPortfolioFilter();
            }
        },

        // 'index.html'deki '.counter' animasyonunu yönetir
        initStatCounters() {
            const counters = document.querySelectorAll('.counter');
            if (counters.length === 0) return;
            console.log('Vitrin Modülü: Sayaçlar başlatılıyor...');

            const animateCounters = (counter) => {
                const target = +counter.getAttribute('data-target');
                let count = 0;
                const speed = 200; // Animasyon hızı (daha küçük = daha hızlı)
                const inc = target / speed;

                const updateCount = () => {
                    if (count < target) {
                        count += inc;
                        if (count > target) count = target;
                        counter.innerText = Math.ceil(count).toLocaleString('tr-TR');
                        setTimeout(updateCount, 10);
                    } else {
                        counter.innerText = target.toLocaleString('tr-TR');
                    }
                };
                updateCount();
            };

            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCounters(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            counters.forEach(counter => {
                counter.innerText = '0';
                observer.observe(counter);
            });
        },
        
        // 'packages.html'deki '#pricing-toggle-switch' anahtarını yönetir
        initPricingToggle() {
            console.log('Vitrin Modülü: Fiyat anahtarı başlatılıyor...');
            const toggleSwitch = document.getElementById('pricing-toggle-switch');
            if (!toggleSwitch) return;

            const monthlyPrices = document.querySelectorAll('.price-monthly');
            const yearlyPrices = document.querySelectorAll('.price-yearly');
    
            toggleSwitch.addEventListener('change', function() {
                const isYearly = this.checked;
                monthlyPrices.forEach(price => price.classList.toggle('d-none', isYearly));
                yearlyPrices.forEach(price => price.classList.toggle('d-none', !isYearly));
            });
        },

        // 'portfolio.html'deki '.portfolio-container' filtresini yönetir
        initPortfolioFilter() {
            console.log('Vitrin Modülü: Portfolyo filtresi (Isotope) başlatılıyor...');
            const portfolioContainer = document.querySelector('.portfolio-container');
            
            imagesLoaded(portfolioContainer, function () {
                const iso = new Isotope(portfolioContainer, {
                    itemSelector: '.portfolio-item',
                    layoutMode: 'fitRows',
                    transitionDuration: '0.6s'
                });
    
                const filterContainer = document.getElementById('portfolio-filters');
                if(filterContainer) {
                    filterContainer.addEventListener('click', function(event) {
                        if (!event.target.matches('.filter-btn')) return;
                        
                        filterContainer.querySelector('.active').classList.remove('active');
                        event.target.classList.add('active');
                        
                        const filterValue = event.target.getAttribute('data-filter');
                        iso.arrange({ filter: filterValue });
    
                        setTimeout(() => {
                            const noResultsItem = portfolioContainer.querySelector('.no-results-item');
                            if (noResultsItem) {
                                noResultsItem.style.display = (iso.filteredItems.length > 0) ? 'none' : 'block';
                            }
                        }, 600);
                    });
                }
            });
        }
    }, // <-- BÖLÜM 2 SONU (Vitrin Modülü bitti)

    /**
     * ===================================================================
     * BÖLÜM 3: ÜYELİK MODÜLÜ (AUTH)
     * login.html ve register.html sayfalarını yönetir.
     * Bu kodlar, o sayfalardaki <script> bloklarını gereksiz kılar (DRY).
     * ===================================================================
     */
    Auth: {
        init() {
            // Sadece .auth-page-wrapper (login/register) sayfalarındaysak çalışır
            if (!document.querySelector('.auth-page-wrapper')) return;
            
            console.log('Üyelik Modülü Yüklendi.');
            this.initPasswordToggle();
            this.initPasswordStrengthMeter();
            this.initPasswordMatch();
            this.initFloatingLabels();
        },

        // 'login.html' ve 'register.html'deki '#togglePassword' ikonunu yönetir
        initPasswordToggle() {
            const togglePassword = document.getElementById('togglePassword');
            // Hem `login` hem de `register` sayfasındaki ID'leri kontrol et
            const passwordInput = document.getElementById('password') || document.getElementById('floatingPassword'); 

            if (togglePassword && passwordInput) {
                togglePassword.addEventListener('click', function () {
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    this.querySelector('i').classList.toggle('fa-eye');
                    this.querySelector('i').classList.toggle('fa-eye-slash');
                });
            }
        },

        // 'register.html'deki '#password-strength-bar' çubuğunu yönetir
        initPasswordStrengthMeter() {
            const passwordInput = document.getElementById('password');
            const strengthBar = document.getElementById('password-strength-bar');
            const strengthText = document.getElementById('password-strength-text');
            
            // Sadece register sayfasındaysak (bu elementler varsa) çalış
            if (!passwordInput || !strengthBar || !strengthText) return;

            console.log('Auth Modülü: Şifre gücü ölçer başlatılıyor...');
            passwordInput.addEventListener('input', () => {
                const password = passwordInput.value;
                let score = 0;
                let feedback = { text: '', color: 'bg-secondary', width: '0%' };

                if (password.length > 0) {
                    if (password.length >= 8) score++;
                    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
                    if (/\d/.test(password)) score++;
                    if (/[^A-Za-z0-9]/.test(password)) score++; // Özel karakter
                
                    switch(score) {
                        case 1: feedback = { text: 'Zayıf', color: 'bg-danger', width: '25%' }; break;
                        case 2: feedback = { text: 'Orta', color: 'bg-warning', width: '50%' }; break;
                        case 3: feedback = { text: 'Güçlü', color: 'bg-success', width: '75%' }; break;
                        case 4: feedback = { text: 'Çok Güçlü', color: 'bg-success', width: '100%' }; break;
                        default: feedback = { text: 'Çok Zayıf', color: 'bg-danger', width: '10%' };
                    }
                }
                
                strengthBar.style.width = feedback.width;
                strengthBar.className = `progress-bar ${feedback.color}`;
                strengthText.textContent = feedback.text;
                // CSS değişkenlerimizden renk alıyoruz (`style.css`'de tanımlı)
                strengthText.style.color = `var(--${feedback.color.replace('bg-','')})`;
            });
        },

        // 'register.html'deki '#password-match-text' alanını yönetir
        initPasswordMatch() {
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm_password');
            const matchText = document.getElementById('password-match-text');

            if (!passwordInput || !confirmPasswordInput || !matchText) return;

            console.log('Auth Modülü: Şifre eşleşme kontrolcüsü başlatılıyor...');
            const checkMatch = () => {
                const password = passwordInput.value;
                const confirmPassword = confirmPasswordInput.value;

                if (confirmPassword.length > 0 && password.length > 0) {
                    if (password === confirmPassword) {
                        matchText.textContent = '✓ Şifreler eşleşiyor.';
                        matchText.style.color = 'var(--success)';
                    } else {
                        matchText.textContent = '✗ Şifreler eşleşmiyor.';
                        matchText.style.color = 'var(--danger)';
                    }
                } else {
                    matchText.textContent = '';
                }
            };
            passwordInput.addEventListener('input', checkMatch);
            confirmPasswordInput.addEventListener('input', checkMatch);
        },

        // Üyelik sayfalarındaki 'floating label' animasyonunu yönetir
        initFloatingLabels() {
            const formFloatingInputs = document.querySelectorAll('.form-floating .form-control');
            formFloatingInputs.forEach(input => {
                input.addEventListener('focus', () => {
                    input.closest('.form-floating').classList.add('is-focused');
                });
                input.addEventListener('blur', () => {
                    input.closest('.form-floating').classList.remove('is-focused');
                });
            });
        }
    }, // <-- BÖLÜM 3 SONU (Auth Modülü bitti)
    /**
     * ===================================================================
     * BÖLÜM 4: PANEL MODÜLÜ
     * `_panel_layout.html`'i kullanan sayfaları yönetir.
     * profile.html, list_users.html, edit_user.html
     * ===================================================================
     */
    Panel: {
        init() {
            // Panel modülü, sadece .panel-wrapper (giriş yapılmış) sayfalarındaysak çalışır
            if (!document.querySelector('.panel-wrapper')) return;
            
            console.log('Panel Modülü Yüklendi.');
            this.initImagePreview();
            this.initDynamicDeleteModal();
            this.initLiveSearch();
            this.initSalesChart();
        },

        // 'profile.html' ve 'edit_user.html'deki #imageUpload önizlemesini yönetir
        initImagePreview() {
            const imageUpload = document.getElementById('imageUpload');
            const imagePreview = document.getElementById('imagePreview');

            if (imageUpload && imagePreview) {
                console.log('Panel Modülü: Resim yükleme önizleyicisi başlatılıyor...');
                imageUpload.addEventListener('change', function(event) {
                    const file = event.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            imagePreview.src = e.target.result;
                        }
                        reader.readAsDataURL(file);
                    }
                });
            }
        },

        // 'list_users.html' ve 'edit_user.html'deki #deleteUserModal'ı dinamik olarak yönetir
        initDynamicDeleteModal() {
            const deleteModal = document.getElementById('deleteUserModal');
            if (deleteModal) {
                console.log('Panel Modülü: Güvenli silme modalı başlatılıyor...');
                deleteModal.addEventListener('show.bs.modal', function (event) {
                    const button = event.relatedTarget; // Modal'ı tetikleyen buton
                    const userId = button.dataset.userId;
                    const userName = button.dataset.userName;
        
                    const form = document.getElementById('deleteUserForm');
                    // Formun action URL'sini dinamik olarak ayarla
                    form.action = `/admin/delete_user/${userId}`;
        
                    const userNameSpan = document.getElementById('userNameToDelete');
                    userNameSpan.textContent = userName;
                });
            }
        },

        // 'list_users.html'deki #user-search-input ile anlık arama yapar
        initLiveSearch() {
            const searchInput = document.getElementById('user-search-input');
            const userTableBody = document.getElementById('user-table-body');
            
            if (searchInput && userTableBody) {
                console.log('Panel Modülü: Personel listesi anlık arama başlatılıyor...');
                const userRows = userTableBody.querySelectorAll('.user-row');
                const noResultsRow = document.getElementById('no-results-row');

                searchInput.addEventListener('keyup', function() {
                    const searchTerm = this.value.toLowerCase().trim();
                    let visibleCount = 0;
        
                    userRows.forEach(row => {
                        // Aramayı daha kapsamlı hale getirdik
                        const name = (row.querySelector('.user-name')?.textContent || '').toLowerCase();
                        const email = (row.querySelector('.user-email')?.textContent || '').toLowerCase();
                        const title = (row.querySelector('.user-title')?.textContent || '').toLowerCase();
                        
                        if (name.includes(searchTerm) || email.includes(searchTerm) || title.includes(searchTerm)) {
                            row.style.display = '';
                            visibleCount++;
                        } else {
                            row.style.display = 'none';
                        }
                    });
        
                    if (noResultsRow) {
                        noResultsRow.classList.toggle('d-none', visibleCount > 0);
                    }
                });
            }
        },

        // 'profile.html'deki #salesChart grafiğini çizer
        initSalesChart() {
            const ctx = document.getElementById('salesChart');
            // 'profile.html' şablonu, backend'den gelen veriyi bu 'data-sales' içine gömer
            if (ctx && ctx.dataset.sales) {
                console.log('Panel Modülü: Satış grafiği (Chart.js) başlatılıyor...');
                try {
                    const monthlySalesData = JSON.parse(ctx.dataset.sales);
                    
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: monthlySalesData.labels,
                            datasets: [{
                                label: 'Aylık Satış Tutarı (₺)',
                                data: monthlySalesData.data,
                                backgroundColor: 'rgba(0, 168, 232, 0.6)',
                                borderColor: 'rgba(0, 168, 232, 1)',
                                borderWidth: 1,
                                borderRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                y: { 
                                    beginAtZero: true,
                                    ticks: { color: 'var(--text-muted)' },
                                    grid: { color: 'var(--border-color)' }
                                },
                                x: {
                                    ticks: { color: 'var(--text-muted)' },
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                } catch (e) {
                    console.error("Satış grafiği verisi okunamadı veya hatalı:", e);
                    ctx.parentElement.innerHTML = '<p class="alert alert-danger text-center">Grafik yüklenirken bir hata oluştu.</p>';
                }
            }
        }
    }, // <-- BÖLÜM 4 SONU (Panel Modülü bitti)

    /**
     * ===================================================================
     * BÖLÜM 5: AKADEMİ MODÜLÜ (LMS)
     * academy.html (dinamik kurs listesi) ve quiz.html (sınav motoru)
     * sayfalarını yönetir. Bu, projenin en karmaşık JS modülüdür.
     * ===================================================================
     */
    Academy: {
        // Tüm kurs verilerini uygulama genelinde saklamak için
        allCourseData: [],

        init() {
            // Sadece ilgili sayfalarda ilgili fonksiyonları çalıştır
            if (document.getElementById('course-grid')) {
                this.initAcademyPlatform();
            }
            // `quiz.html`'den gelen `window.quizQuestions` değişkenini kontrol et
            if (typeof window.quizQuestions !== 'undefined' && window.quizQuestions.length > 0) {
                this.initQuiz();
            }
        },

        // --- 5.1 AKADEMİ ANA PLATFORMU ---
        // 'academy.html' sayfasını yönetir
        initAcademyPlatform() {
            console.log('Akademi Modülü: Dinamik kurs platformu başlatılıyor...');
            
            // Gerekli tüm DOM elementlerini seç ve `this`'e bağla
            this.grid = document.getElementById('course-grid');
            this.template = document.getElementById('course-card-template');
            this.noResults = document.getElementById('no-results');
            
            this.searchInput = document.getElementById('search-input');
            this.categoryFilter = document.getElementById('category-filter');
            this.difficultyFilter = document.getElementById('difficulty-filter');
            this.sortBy = document.getElementById('sort-by');
            
            // Tüm olay dinleyicilerini (arama, filtreleme, sıralama) tek seferde bağla
            [this.searchInput, this.categoryFilter, this.difficultyFilter, this.sortBy].forEach(el => {
                if(el) el.addEventListener('input', () => this.renderCourses());
            });

            // Sayfa ilk yüklendiğinde veriyi backend'den çek
            this.fetchCourseData();
        },

        // Backend'deki '/academy/data' API rotasından JSON verisini çeker
        async fetchCourseData() {
            if (!this.grid) return;
            this.grid.innerHTML = '<div class="col-12 text-center p-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
            try {
                // Python'da oluşturduğumuz '/academy/data' adresine istek atıyoruz
                // Bu URL'yi 'academy.html' şablonunda bir data-url olarak saklamak daha iyidir
                const response = await fetch("/academy/data"); 
                if (!response.ok) throw new Error(`HTTP hatası! Durum: ${response.status}`);
                
                const data = await response.json();
                this.allCourseData = data; // Gelen veriyi saklıyoruz
                
                this.populateCategories(this.allCourseData); // Kategori filtresini dinamik olarak doldur
                this.renderCourses(); // Sayfayı ilk kez render et (ekrana bas)
            } catch (error) {
                console.error("Kurs verileri alınamadı:", error);
                this.grid.innerHTML = `<div class="col-12 text-center p-5"><i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i><h5 class="text-white">Kurslar yüklenemedi.</h5><p class="text-muted">Bir sorun oluştu. Lütfen daha sonra tekrar deneyin.</p></div>`;
            }
        },

        // JSON verisinden kategori filtresini dinamik olarak oluşturur
        populateCategories(courses) {
            if (!this.categoryFilter) return;
            const categories = [...new Set(courses.map(course => course.category))];
            this.categoryFilter.innerHTML = '<option value="all">Tüm Kategoriler</option>';
            categories.sort().forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                this.categoryFilter.appendChild(option);
            });
        },

        // Kursları filtreler, sıralar ve 'academy.html' şablonuna basar
        renderCourses() {
            if (!this.grid) return;
            
            const searchTerm = this.searchInput.value.toLowerCase();
            const selectedCategory = this.categoryFilter.value;
            const selectedDifficulty = this.difficultyFilter.value;
            const sortValue = this.sortBy.value;

            // 1. FİLTRELEME
            let filteredCourses = this.allCourseData.filter(course => {
                const matchesSearch = course.title.toLowerCase().includes(searchTerm) || course.description.toLowerCase().includes(searchTerm);
                const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
                const matchesDifficulty = selectedDifficulty === 'all' || course.difficulty === selectedDifficulty;
                return matchesSearch && matchesCategory && matchesDifficulty;
            });

            // 2. SIRALAMA
            filteredCourses.sort((a, b) => {
                switch (sortValue) {
                    case 'title-asc': return a.title.localeCompare(b.title, 'tr');
                    case 'title-desc': return b.title.localeCompare(a.title, 'tr');
                    case 'progress-desc': return b.enrollment.progress - a.enrollment.progress;
                    case 'progress-asc': return a.enrollment.progress - b.enrollment.progress;
                    default: return 0;
                }
            });

            this.grid.innerHTML = ''; 
            this.noResults.classList.toggle('d-none', filteredCourses.length > 0);

            // 3. RENDER ETME
            filteredCourses.forEach(course => {
                const card = this.template.content.cloneNode(true); // HTML şablonunu kopyala
                
                // Kopyalanan şablonu JSON verisiyle doldur
                // Not: 'images/courses/' yolu, 'academy_routes.py'deki 'save_picture'
                // fonksiyonunda belirtilen 'folder' ile eşleşmelidir.
                const imgEl = card.querySelector('.course-image');
                if (course.cover_image && (course.cover_image.startsWith('http://') || course.cover_image.startsWith('https://'))) {
                    imgEl.src = course.cover_image;
                } else {
                    imgEl.src = `/static/uploads/courses/${course.cover_image}`;
                }
                card.querySelector('.course-category').textContent = course.category;
                card.querySelector('.course-title').textContent = course.title;
                card.querySelector('.course-description').textContent = course.description.substring(0, 100) + '...';
                card.querySelector('.course-difficulty').innerHTML = `<i class="fas fa-signal me-2"></i>${course.difficulty}`;
                card.querySelector('.course-duration').innerHTML = `<i class="fas fa-clock me-2"></i>${course.duration_hours} Saat`;
                
                const link = card.querySelector('.course-link');
                link.href = `/academy/course/${course.id}`;

                const progressContainer = card.querySelector('.course-progress-container');
                if (course.enrollment.is_enrolled) {
                    const progressBar = card.querySelector('.course-progress-bar');
                    progressBar.style.width = `${course.enrollment.progress}%`;
                    progressBar.setAttribute('aria-valuenow', course.enrollment.progress);
                    if (course.enrollment.progress > 10) {
                         progressBar.textContent = `${course.enrollment.progress}%`;
                    }
                    link.textContent = 'Kursa Devam Et';
                } else {
                    progressContainer.style.display = 'none';
                    link.textContent = 'Detayları Gör';
                    link.classList.replace('btn-primary', 'btn-outline-primary');
                }
                
                this.grid.appendChild(card); // Doldurulmuş kartı ekrana ekle
            });
        },

        // --- 5.2 OYUNLAŞTIRILMIŞ SINAV PLATFORMU ---
        // 'quiz.html' sayfasını yönetir
        initQuiz() {
            const quizCard = document.getElementById('quiz-card');
            if (!quizCard) return;

            console.log('Akademi Modülü: Oyunlaştırılmış Sınav Motoru başlatılıyor...');
            
            // `quiz.html`'den gelen `window.quizQuestions` global değişkeninden soruları al
            this.quizData = window.quizQuestions || [];
            if(this.quizData.length === 0) {
                console.error("Sınav başlatılamadı: 'window.quizQuestions' boş.");
                return;
            }

            this.quizElements = {
                card: quizCard,
                questionText: document.getElementById('question-text'),
                answerOptions: document.getElementById('answer-options'),
                nextBtn: document.getElementById('next-btn'),
                progressBar: document.getElementById('progress-bar'),
                counter: document.getElementById('question-counter'),
                resultModal: new bootstrap.Modal(document.getElementById('quiz-result-modal')),
                scoreForm: document.getElementById('submit-score-form'),
                explanationDiv: document.getElementById('answer-explanation'),
                explanationText: document.getElementById('explanation-text')
            };
            
            this.currentQuestionIndex = 0;
            this.score = 0;
            this.isAnswered = false;

            // Ses efektleri için synth oluştur (Tone.js 'layout.html'de yüklü olmalı)
            if (typeof Tone !== 'undefined') {
                this.synth = new Tone.Synth().toDestination();
            } else {
                console.warn("Tone.js yüklenemedi, sınav ses efektleri çalışmayacak.");
                // Sahte bir playSound fonksiyonu oluştur
                this.synth = { playSound: () => {} };
            }

            // Olay dinleyicilerini bağla
            this.quizElements.nextBtn.addEventListener('click', () => this.handleNextClick());
            document.getElementById('retry-quiz-btn').addEventListener('click', () => window.location.reload());

            this.loadQuestion(); // Sınavı başlat
        },

        // Doğru/yanlış sesini oynatır
        playSound(isCorrect) {
            if (typeof Tone === 'undefined') return;
            Tone.start().then(() => {
                const note = isCorrect ? "C5" : "C3";
                const duration = isCorrect ? "8n" : "4n";
                this.synth.triggerAttackRelease(note, duration);
            });
        },

        // Mevcut soruyu ve seçeneklerini ekrana yükler
        loadQuestion() {
            this.isAnswered = false;
            const currentQuestion = this.quizData[this.currentQuestionIndex];
            const elements = this.quizElements;

            elements.questionText.textContent = currentQuestion.question;
            elements.counter.textContent = `Soru ${this.currentQuestionIndex + 1} / ${this.quizData.length}`;
            const progress = (this.currentQuestionIndex / this.quizData.length) * 100;
            elements.progressBar.style.width = `${progress}%`;
            
            // Seçenekleri rastgele sırala (Fisher-Yates shuffle algoritması)
            const shuffledOptions = [...currentQuestion.options];
            const correctAnswer = shuffledOptions[currentQuestion.correct_index];
            
            // Shuffle işlemi
            for (let i = shuffledOptions.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [shuffledOptions[i], shuffledOptions[j]] = [shuffledOptions[j], shuffledOptions[i]];
            }
            
            // Doğru cevabın yeni indeksini bul ve güncelle
            const newCorrectIndex = shuffledOptions.indexOf(correctAnswer);
            currentQuestion.shuffledCorrectIndex = newCorrectIndex;
            
            elements.answerOptions.innerHTML = '';
            shuffledOptions.forEach((option, index) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'list-group-item list-group-item-action answer-option';
                button.textContent = option;
                button.dataset.index = index;
                button.addEventListener('click', (e) => this.handleAnswerClick(e));
                elements.answerOptions.appendChild(button);
            });

            // Açıklama alanını gizle
            if (elements.explanationDiv) {
                elements.explanationDiv.classList.add('d-none');
            }
            elements.nextBtn.classList.add('d-none');
        },

        // Bir cevaba tıklandığında çalışır
        handleAnswerClick(event) {
            if (this.isAnswered) return;
            this.isAnswered = true;

            const selectedBtn = event.target;
            const selectedIndex = parseInt(selectedBtn.dataset.index);
            // Shuffle edilmiş seçenekler için doğru indeksi kullan
            const correctIndex = this.quizData[this.currentQuestionIndex].shuffledCorrectIndex !== undefined 
                ? this.quizData[this.currentQuestionIndex].shuffledCorrectIndex 
                : this.quizData[this.currentQuestionIndex].correct_index;

            // Skoru backend'e göndermek için gizli input oluştur
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = `question-${this.currentQuestionIndex}`;
            hiddenInput.value = selectedIndex;
            this.quizElements.scoreForm.appendChild(hiddenInput);
            
            // Seçilen seçeneğin metnini de gönder (backend'de doğrulama için)
            const selectedOptionText = selectedBtn.textContent.trim();
            const textInput = document.createElement('input');
            textInput.type = 'hidden';
            textInput.name = `question-${this.currentQuestionIndex}-text`;
            textInput.value = selectedOptionText;
            this.quizElements.scoreForm.appendChild(textInput);

            // Cevabı kontrol et ve görsel/sesli geri bildirim ver
            const isCorrect = selectedIndex === correctIndex;
            if (isCorrect) {
                this.score++;
                selectedBtn.classList.add('correct');
                this.playSound(true);
            } else {
                selectedBtn.classList.add('incorrect');
                this.playSound(false);
                const correctBtn = this.quizElements.answerOptions.querySelector(`[data-index="${correctIndex}"]`);
                if(correctBtn) correctBtn.classList.add('correct');
            }

            // Açıklama göster (varsa)
            const currentQuestion = this.quizData[this.currentQuestionIndex];
            if (this.quizElements.explanationDiv && this.quizElements.explanationText) {
                if (currentQuestion.explanation) {
                    this.quizElements.explanationText.textContent = currentQuestion.explanation;
                    this.quizElements.explanationDiv.classList.remove('d-none');
                    // Açıklama rengini cevaba göre ayarla
                    const alertDiv = this.quizElements.explanationDiv.querySelector('.alert');
                    if (alertDiv) {
                        if (isCorrect) {
                            alertDiv.className = 'alert alert-success bg-success bg-opacity-10 border-success border-opacity-50';
                        } else {
                            alertDiv.className = 'alert alert-warning bg-warning bg-opacity-10 border-warning border-opacity-50';
                        }
                    }
                } else {
                    // Varsayılan açıklama
                    if (isCorrect) {
                        this.quizElements.explanationText.textContent = 'Tebrikler! Doğru cevap. Bu konuyu iyi anlamışsınız.';
                        const alertDiv = this.quizElements.explanationDiv.querySelector('.alert');
                        if (alertDiv) {
                            alertDiv.className = 'alert alert-success bg-success bg-opacity-10 border-success border-opacity-50';
                        }
                    } else {
                        // shuffledOptions'ı doğru şekilde al
                        const currentQuestion = this.quizData[this.currentQuestionIndex];
                        const shuffledOptions = [...currentQuestion.options];
                        // Doğru cevabın indeksini bul
                        const correctAnswerIndex = currentQuestion.shuffledCorrectIndex !== undefined 
                            ? currentQuestion.shuffledCorrectIndex 
                            : currentQuestion.correct_index;
                        const correctAnswer = shuffledOptions[correctAnswerIndex];
                        this.quizElements.explanationText.textContent = `Doğru cevap: "${correctAnswer}". Bu konuyu tekrar gözden geçirmenizi öneririz.`;
                        const alertDiv = this.quizElements.explanationDiv.querySelector('.alert');
                        if (alertDiv) {
                            alertDiv.className = 'alert alert-warning bg-warning bg-opacity-10 border-warning border-opacity-50';
                        }
                    }
                    this.quizElements.explanationDiv.classList.remove('d-none');
                }
            }

            // Tüm cevap butonlarını devre dışı bırak
            this.quizElements.answerOptions.querySelectorAll('.answer-option').forEach(btn => {
                btn.disabled = true;
                btn.style.cursor = 'not-allowed';
            });
            
            // Sonraki soru butonunu göster ve aktif et (yanlış cevapta da)
            this.quizElements.nextBtn.textContent = (this.currentQuestionIndex < this.quizData.length - 1) ? 'Sonraki Soru' : 'Sınavı Bitir';
            this.quizElements.nextBtn.classList.remove('d-none');
            this.quizElements.nextBtn.disabled = false;
        },

        // "Sonraki" butonuna tıklandığında çalışır
        handleNextClick() {
            if (this.currentQuestionIndex < this.quizData.length - 1) {
                this.currentQuestionIndex++;
                this.loadQuestion();
            } else {
                this.showResults();
            }
        },

        // Sınav bitince sonuçları gösterir
        showResults() {
            this.quizElements.progressBar.style.width = `100%`;
            const total = this.quizData.length;
            const percentage = Math.round((this.score / total) * 100);
            
            const iconEl = document.getElementById('result-icon');
            const titleEl = document.getElementById('result-title');
            const messageEl = document.getElementById('result-message');
            const scoreEl = document.getElementById('score-text');

            scoreEl.textContent = `${this.score} / ${total} (%${percentage})`;
            iconEl.className = 'fas fa-4x mb-3'; // Önceki sınıfları temizle

            if (percentage >= 80) {
                iconEl.classList.add('fa-trophy', 'text-warning');
                titleEl.textContent = 'Harika İş!';
                messageEl.textContent = 'Bu konuya tamamen hakimsin. Tebrikler!';
            } else if (percentage >= 50) {
                iconEl.classList.add('fa-check-circle', 'text-success');
                titleEl.textContent = 'İyi Gidiyorsun!';
                messageEl.textContent = 'Konunun temellerini anladın, ancak birkaç noktayı tekrar gözden geçirebilirsin.';
            } else {
                iconEl.classList.add('fa-redo-alt', 'text-danger');
                titleEl.textContent = 'Tekrar Denemelisin';
                messageEl.textContent = 'Endişelenme, bu bir öğrenme süreci. Dersi tekrar edip yeniden denemek en iyisi olacaktır.';
            }
            
            // Frontend skorunu backend'e göndermek için gizli input ekle
            const frontendScoreInput = document.createElement('input');
            frontendScoreInput.type = 'hidden';
            frontendScoreInput.name = 'frontend_score';
            frontendScoreInput.value = this.score;
            this.quizElements.scoreForm.appendChild(frontendScoreInput);
            
            // Sonuç modal'ını göster. Form, modal içindeki butona basılınca gönderilecek.
            this.quizElements.resultModal.show();
        }
    } // <-- BÖLÜM 5 SONU (Academy Modülü bitti)

}; // <-- KuwamedyaApp NESNESİNİN SONU

// ===================================================================
// UYGULAMAYI BAŞLAT
// ===================================================================
KuwamedyaApp.init();

