@echo off
echo KairoAI Service Installation Script
echo ================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Install the service
echo Installing KairoAI Service...
python windows_service.py install

REM Set service to auto-start
echo Configuring service to start automatically...
sc config KairoAI start= auto

REM Start the service
echo Starting KairoAI Service...
python windows_service.py start

echo.
echo Installation complete!
echo.
echo To manage the service, use these commands:
echo - Start: python windows_service.py start
echo - Stop: python windows_service.py stop
echo - Restart: python windows_service.py restart
echo - Remove: python windows_service.py remove
echo.
echo Service status can be checked at:
echo - Health: http://localhost:5000/health
echo - Status: http://localhost:5000/status
echo - Environment: http://localhost:5000/environment
echo.

pause 