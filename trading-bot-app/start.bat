@echo off
title Trading Bot - Starting Services
echo ==========================================
echo  Trading Bot App - Starting Services
echo ==========================================
echo.

REM First, stop any existing instances
echo [PRE-CHECK] Stopping any existing services...
call stop.bat >nul 2>&1

echo.
echo [1/4] Checking installation...
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run 'install.bat' first.
    pause
    exit /b 1
)
echo Virtual environment found.

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Creating storage directories if needed...
if not exist "storage" mkdir storage
if not exist "storage\strategies" mkdir storage\strategies
if not exist "storage\logs" mkdir storage\logs
if not exist "storage\shadow_trades" mkdir storage\shadow_trades
if not exist "storage\backtests" mkdir storage\backtests

echo.
echo [4/4] Starting services...
echo.

REM Start the main trading bot in a new window
echo Starting Trading Bot Engine...
start "Trading Bot - Strategy Engine" cmd /k "title Trading Bot - Strategy Engine & call venv\Scripts\activate.bat & python src/main.py"

REM Wait a moment for bot to initialize
timeout /t 3 /nobreak >nul

REM Start the dashboard in a new window
echo Starting Web Dashboard...
start "Trading Bot - Dashboard" cmd /k "title Trading Bot - Dashboard & call venv\Scripts\activate.bat & python src/dashboard/app.py"

echo.
echo ==========================================
echo  SERVICES STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo Two windows should have opened:
echo 1. Trading Bot - Strategy Engine (background learning & trading)
echo 2. Trading Bot - Dashboard (web interface)
echo.
echo Dashboard URL: http://localhost:5000
echo.
echo To stop all services, run 'stop.bat'
echo To uninstall, run 'uninstall.bat'
echo.
echo Press any key to close this window...
pause >nul
