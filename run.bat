@echo off
setlocal EnableDelayedExpansion

title FindUrCite Launcher
cd /d "%~dp0"

echo ===================================================
echo       FindUrCite - One-Click Installer ^& Runner
echo ===================================================

:: 1. Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b
)

:: 2. Setup Virtual Environment
echo [2/6] Checking Virtual Environment...
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: 3. Install Dependencies
echo [3/6] Installing/Updating dependencies...
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

:: 4. Check & Install Ollama
echo [4/6] Checking Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama not found. Attempting to install via Winget...
    winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Ollama. Please download manually from https://ollama.com/
        pause
        exit /b
    )
    echo [INFO] Ollama installed. Please RESTART this script to ensure PATH is updated.
    echo [INFO] You may need to reopen the terminal.
    pause
    exit /b
)

:: 5. Check Ollama Service & Model
echo [5/6] Checking AI Model (qwen2.5:7b)...

:: Check if Ollama service is responsive
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Ollama service is not running. Starting background service...
    start /B ollama serve
    echo [INFO] Waiting for Ollama to initialize...
    timeout /t 10 >nul
)

:: Check for model
ollama list | findstr "qwen2.5:7b" >nul
if %errorlevel% neq 0 (
    echo [INFO] Model not found. Downloading qwen2.5:7b...
    echo [INFO] This process depends on your internet speed. Please wait...
    ollama pull qwen2.5:7b
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to pull model. Please check your internet connection.
        pause
        exit /b
    )
)

:: 6. Start Server
echo [6/6] Starting FindUrCite Server...
echo [INFO] Server will run at http://localhost:8000
echo [INFO] Press Ctrl+C to stop the server.

start http://localhost:8000
python src/server.py

pause
