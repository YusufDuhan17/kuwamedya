@echo off
REM ============================================================================
REM KUWAMEDYA - Development Mode (Debug Açık)
REM ============================================================================
REM Bu script debug modunda çalıştırır (geliştirme için)
REM ============================================================================

echo.
echo ========================================
echo   KUWAMEDYA - Development Mode
echo   (Debug Modu Aktif)
echo ========================================
echo.

REM Sanal ortam kontrolü
if not exist "venv\Scripts\activate.bat" (
    echo [HATA] Sanal ortam bulunamadi!
    pause
    exit /b 1
)

REM Sanal ortamı aktifleştir
call venv\Scripts\activate.bat

REM Debug modunu ayarla ve başlat
set FLASK_ENV=dev
set FLASK_DEBUG=1

echo Tarayici 3 saniye icinde acilacak...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5000

echo.
echo Flask uygulamasi baslatiliyor (Debug modu)...
echo.

flask run --debug

