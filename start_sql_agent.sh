#!/bin/bash
# ========================================
# SQL Agent - Linux/Mac Startup Script
# ========================================

echo "========================================"
echo "SQL Agent Startup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Python version check..."
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
else
    echo "[2/4] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo ""

# Install/Update requirements
echo "[4/4] Installing required packages..."
pip install -r requirements_fixed.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi
echo ""

echo "========================================"
echo "All dependencies installed successfully!"
echo "========================================"
echo ""
echo "Starting SQL Agent Web Application..."
echo ""
echo "IMPORTANT: You will need to provide your OpenAI API key in the web interface"
echo ""
echo "Opening browser at: http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""

# Start the application
python3 web_app_fixed.py
