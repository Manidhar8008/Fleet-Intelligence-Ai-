@echo off
REM Fleet Intelligence AI - Windows Run Script
REM Production-ready startup script with safety checks

setlocal enabledelayedexpansion

echo.
echo ==================================================
echo   Fleet Intelligence AI - Starting...
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.9 or higher.
    echo   Get it from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo X Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo X Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo [SETUP] Installing dependencies (this may take a minute)...
pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo X Failed to install dependencies
    echo   Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check for sample data
if not exist "data\sample_fleet.csv" (
    echo [WARNING] Sample data not found at data\sample_fleet.csv
    echo           You can upload data via the Streamlit interface or add sample_fleet.csv
    echo.
)

REM Run Streamlit app
echo.
echo ==================================================
echo   Launching Fleet Intelligence AI
echo ==================================================
echo   Opening at: http://localhost:8501
echo   Press Ctrl+C to stop the server
echo ==================================================
echo.

streamlit run main.py --logger.level=info

pause
