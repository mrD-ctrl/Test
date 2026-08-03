@echo off
echo ==========================================
echo  Trading Bot App - Uninstallation Script
echo ==========================================
echo.
echo WARNING: This will remove all installed files!
echo Your .env file and storage data will be DELETED.
echo.
set /p confirm="Are you sure you want to continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/5] Stopping all running services...
call stop.bat >nul 2>&1
echo Services stopped.

echo.
echo [2/5] Removing virtual environment...
if exist "venv" (
    rmdir /s /q "venv"
    echo Virtual environment removed.
) else (
    echo No virtual environment found.
)

echo.
echo [3/5] Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /q /s *.pyc >nul 2>&1
echo Cache files removed.

echo.
echo [4/5] Removing storage data (strategies, logs, trades)...
if exist "storage" (
    rmdir /s /q "storage"
    echo Storage directory removed.
) else (
    echo No storage directory found.
)

echo.
echo [5/5] Removing configuration files...
if exist ".env" del /q ".env"
echo Configuration files removed.

echo.
echo NOTE: The following files are KEPT for your reference:
echo - install.bat, start.bat, stop.bat, uninstall.bat
echo - requirements.txt
echo - Source code (src folder)
echo - Documentation files
echo.
echo To reinstall later, simply run 'install.bat' again.
echo.
echo ==========================================
echo  UNINSTALLATION COMPLETED
echo ==========================================
echo.
pause
