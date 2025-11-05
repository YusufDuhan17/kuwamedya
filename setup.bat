@echo off
chcp 65001 >nul
REM ============================================================================
REM KUWAMEDYA - Kurulum Script'i
REM ============================================================================
REM Bu dosya projeyi ilk kurarken veya başka bir klasöre taşıdığınızda çalıştırın.
REM Mevcut kurulumları korur, sadece eksik şeyleri tamamlar.
REM ============================================================================

echo.
echo ========================================
echo   KUWAMEDYA - Kurulum
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo Lutfen Python 3.8+ yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Python kontrol edildi - OK
echo.

REM Sanal ortam kontrolü - varsa kullan, yoksa oluştur
if exist "venv\Scripts\activate.bat" (
    echo [2/6] Sanal ortam zaten mevcut - OK
    echo [3/6] Sanal ortam kontrol ediliyor...
) else (
    echo [2/6] Sanal ortam bulunamadi, olusturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi!
        pause
        exit /b 1
    )
    echo [3/6] Sanal ortam olusturuldu - OK
)
echo.

REM Sanal ortamı aktifleştir
echo [4/6] Sanal ortam aktiflestiriliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [HATA] Sanal ortam aktiflestirilemedi!
    pause
    exit /b 1
)
echo.

REM Pip'i güncelle (sessiz mod)
echo [5/6] Pip kontrol ediliyor...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet >nul 2>&1
echo Pip guncellendi - OK
echo.

REM Bağımlılıkları kontrol et ve sadece eksikleri yükle
echo [6/6] Bagimliliklari kontrol ediliyor...
if not exist "requirements.txt" (
    echo [HATA] requirements.txt dosyasi bulunamadi!
    pause
    exit /b 1
)

REM Flask'in yüklü olup olmadığını kontrol et
venv\Scripts\python.exe -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo Paketler yuklu degil, yukleniyor...
    echo Bu islem birkac dakika surebilir...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [HATA] Paketler yuklenirken hata olustu!
        pause
        exit /b 1
    )
    echo Bagimliliklar yuklendi - OK
) else (
    echo Paketler zaten yuklu - OK
    echo Eksik paketler kontrol ediliyor...
    venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
    echo Kontrol tamamlandi - OK
)
echo.

REM .env dosyası kontrolü
if not exist ".env" (
    echo.
    echo [EK] .env dosyasi olusturuluyor...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo .env dosyasi .env.example'dan olusturuldu.
        echo.
        echo !!! ONEMLI: .env dosyasini duzenleyip SECRET_KEY'i degistirin !!!
        echo.
    ) else (
        echo .env.example dosyasi bulunamadi. Manuel olarak .env olusturun.
    )
)

REM Veritabanı klasörü oluştur
if not exist "instance" mkdir instance

REM Veritabanı kontrolü - yoksa oluştur
if not exist "instance\kuwamedyadb-dev.db" (
    echo.
    echo [EK] Veritabani olusturuluyor ve ornek verilerle dolduruluyor...
    venv\Scripts\python.exe -m flask db upgrade
    if errorlevel 1 (
        echo [UYARI] Veritabani olusturulamadi, devam ediliyor...
    ) else (
        venv\Scripts\python.exe -m flask seed
        if errorlevel 1 (
            echo [UYARI] Seed komutu calistirilamadi, devam ediliyor...
        )
    )
    echo.
) else (
    echo [EK] Veritabani zaten mevcut - OK
    echo.
)

echo ========================================
echo   Kurulum tamamlandi!
echo ========================================
echo.
echo Uygulama baslatiliyor...
echo.

REM 2 saniye bekle
timeout /t 2 /nobreak >nul

REM start.bat dosyasını çalıştır
if exist "start.bat" (
    call start.bat
) else (
    echo [UYARI] start.bat dosyasi bulunamadi!
    echo Manuel olarak uygulamayi baslatin:
    echo   venv\Scripts\activate
    echo   flask run
    echo.
    pause
)

