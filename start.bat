@echo off
chcp 65001 >nul
REM ============================================================================
REM KUWAMEDYA - Otomatik Başlatma Script'i
REM ============================================================================
REM Bu dosyayı çift tıklayarak uygulamayı başlatabilirsiniz.
REM ============================================================================

REM Script'in bulunduğu dizine geç
cd /d "%~dp0"

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
if errorlevel 1 (
    echo [HATA] Sanal ortam aktiflestirilemedi!
    pause
    exit /b 1
)

REM Flask'in yüklü olup olmadığını kontrol et (venv içindeki python ile)
venv\Scripts\python.exe -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo [HATA] Flask yuklu degil!
    echo.
    echo Lutfen once setup.bat dosyasini calistirin.
    echo Veya manuel olarak: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Veritabanı kontrolü (sadece kontrol, kurulum yapmaz)
if not exist "instance\kuwamedyadb-dev.db" (
    echo [2/3] Veritabani bulunamadi!
    echo.
    echo [UYARI] Veritabani olusturulmamis. 
    echo Lutfen once setup.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
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
venv\Scripts\python.exe -m flask run
if errorlevel 1 (
    echo.
    echo [HATA] Flask uygulamasi baslatilamadi!
    echo.
    echo Lutfen hata mesajini kontrol edin.
    pause
    exit /b 1
)

