@echo off
REM ============================================================================
REM KUWAMEDYA - İlk Kurulum Script'i
REM ============================================================================
REM Bu dosyayı sadece İLK KURULUM için çalıştırın!
REM ============================================================================

echo.
echo ========================================
echo   KUWAMEDYA - İlk Kurulum
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

echo [1/5] Python kontrol edildi - OK
echo.

REM Sanal ortam oluştur
if not exist "venv" (
    echo [2/5] Sanal ortam olusturuluyor...
    python -m venv venv
    echo Sanal ortam olusturuldu - OK
) else (
    echo [2/5] Sanal ortam zaten mevcut - OK
)
echo.

REM Sanal ortamı aktifleştir
echo [3/5] Sanal ortam aktiflestiriliyor...
call venv\Scripts\activate.bat
echo.

REM Pip'i güncelle
echo [4/5] Pip guncelleniyor...
python -m pip install --upgrade pip
echo.

REM Bağımlılıkları yükle
echo [5/5] Bagimliliklari yukleniyor...
echo Bu islem birkac dakika surebilir...
pip install -r requirements.txt
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
echo Simdi yapmaniz gerekenler:
echo   1. .env dosyasini duzenleyin (SECRET_KEY'i degistirin)
echo   2. start.bat dosyasini calistirarak uygulamayi baslatin
echo.
pause

