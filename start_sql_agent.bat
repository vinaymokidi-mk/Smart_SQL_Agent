@echo off
REM ========================================
REM SQL Agent - Windows Startup Script
REM ========================================

echo ========================================
echo SQL Agent Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python version check...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo [2/4] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install/Update requirements
echo [4/4] Installing required packages...
pip install -r requirements_fixed.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo.

echo ========================================
echo All dependencies installed successfully!
echo ========================================
echo.
echo Starting SQL Agent Web Application...
echo.
echo IMPORTANT: You will need to provide your OpenAI API key in the web interface
echo.
echo Opening browser at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Start the application
python web_app_fixed.py

pause
