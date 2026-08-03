@echo off
echo ==========================================
echo  Trading Bot App - Stopping Services
echo ==========================================
echo.

echo [1/2] Searching for running trading bot processes...
taskkill /F /FI "WINDOWTITLE eq Trading Bot*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Trading Bot*" >nul 2>&1

echo [2/2] Checking for dashboard process on port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Found process on port 5000, PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo Successfully stopped dashboard process.
    ) else (
        echo Could not stop process (may already be stopped).
    )
    goto :continue
)
echo No dashboard process found on port 5000.

:continue
echo.
echo Cleaning up PID files...
if exist "storage\bot.pid" del /q "storage\bot.pid"
if exist "storage\dashboard.pid" del /q "storage\dashboard.pid"

echo.
echo ==========================================
echo  ALL SERVICES STOPPED SUCCESSFULLY
echo ==========================================
echo.
pause
