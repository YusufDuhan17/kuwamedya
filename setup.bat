@echo off
chcp 65001 >nul
REM ============================================================================
REM KUWAMEDYA - Kurulum Script'i
REM ============================================================================
REM Bu dosya projeyi ilk kurarken veya başka bir klasöre taşıdığınızda çalıştırın.
REM Eski sanal ortamı siler, yenisini oluşturur ve paketleri yükler.
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

REM Eski sanal ortamı sil
if exist "venv" (
    echo [2/6] Eski sanal ortam siliniyor...
    echo Bu islem birkac saniye surebilir...
    rmdir /s /q venv 2>nul
    if exist "venv" (
        echo [UYARI] venv klasoru silinemedi. Manuel olarak silin ve tekrar deneyin.
        pause
        exit /b 1
    )
    echo Eski sanal ortam silindi - OK
) else (
    echo [2/6] Eski sanal ortam bulunamadi - OK
)
echo.

REM Yeni sanal ortam oluştur
echo [3/6] Yeni sanal ortam olusturuluyor...
python -m venv venv
if errorlevel 1 (
    echo [HATA] Sanal ortam olusturulamadi!
    pause
    exit /b 1
)
echo Sanal ortam olusturuldu - OK
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

REM Pip'i güncelle
echo [5/6] Pip guncelleniyor...
python -m pip install --upgrade pip --quiet
echo Pip guncellendi - OK
echo.

REM Bağımlılıkları yükle
echo [6/6] Bagimliliklari yukleniyor...
echo Bu islem birkac dakika surebilir...
if not exist "requirements.txt" (
    echo [HATA] requirements.txt dosyasi bulunamadi!
    pause
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    echo [HATA] Paketler yuklenirken hata olustu!
    pause
    exit /b 1
)
echo Bagimliliklar yuklendi - OK
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

echo.
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

