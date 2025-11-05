@echo off
REM ============================================================================
REM KUWAMEDYA - Otomatik Başlatma Script'i
REM ============================================================================
REM Bu dosyayı çift tıklayarak uygulamayı başlatabilirsiniz.
REM ============================================================================

echo.
echo ========================================
echo   KUWAMEDYA - Uygulama Başlatılıyor...
echo ========================================
echo.

REM Sanal ortamın var olup olmadığını kontrol et
if not exist "venv\Scripts\activate.bat" (
    echo [HATA] Sanal ortam bulunamadi!
    echo.
    echo Lutfen once sanal ortami olusturun:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Sanal ortamı aktifleştir
echo [1/3] Sanal ortam aktiflestiriliyor...
call venv\Scripts\activate.bat

REM Veritabanı kontrolü (isteğe bağlı - ilk kurulum için)
if not exist "instance\kuwamedyadb-dev.db" (
    echo [2/3] Veritabani bulunamadi. Olusturuluyor...
    echo.
    echo Veritabani seed komutu calistiriliyor (ornek verilerle doldurma)...
    flask db upgrade
    flask seed
    echo.
) else (
    echo [2/3] Veritabani kontrol edildi - OK
)

REM Uygulamayı başlat
echo [3/3] Flask uygulamasi baslatiliyor...
echo.
echo ========================================
echo   Uygulama http://127.0.0.1:5000 adresinde calisiyor
echo   Tarayici otomatik olarak acilacak...
echo.
echo   Durdurmak icin bu pencereyi kapatin veya Ctrl+C basin
echo ========================================
echo.

REM Tarayıcıyı Flask başladıktan sonra açmak için arka planda başlat
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000"

REM Flask uygulamasını başlat (bu komut çalışırken tarayıcı açılacak)
flask run

