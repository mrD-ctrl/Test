@echo off
echo ==========================================
echo  Trading Bot App - Installation Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python detected...
python --version

echo.
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [4/4] Creating necessary directories...
if not exist "storage" mkdir storage
if not exist "storage\strategies" mkdir storage\strategies
if not exist "storage\logs" mkdir storage\logs
if not exist "storage\shadow_trades" mkdir storage\shadow_trades
if not exist "storage\backtests" mkdir storage\backtests

echo.
echo [5/5] Creating default .env file...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from template.
) else (
    echo .env file already exists. Keeping current settings.
)

echo.
echo ==========================================
echo  INSTALLATION COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file to add your API keys (optional for shadow mode)
echo 2. Run 'start.bat' to launch the trading bot and dashboard
echo.
pause
