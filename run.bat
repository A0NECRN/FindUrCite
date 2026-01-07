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
    echo [WARN] Ollama not found.
    
    echo [INFO] Attempting to install via Winget...
    winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
    
    if !errorlevel! neq 0 (
        echo [WARN] Winget installation failed. Attempting direct download...
        echo [INFO] Downloading OllamaSetup.exe...
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
        
        if exist "OllamaSetup.exe" (
             echo [INFO] Installer downloaded. Launching...
             echo [INFO] Please complete the installation in the new window.
             start /wait OllamaSetup.exe
             del OllamaSetup.exe
        ) else (
             echo [ERROR] Failed to download Ollama. Please install manually from https://ollama.com/
             pause
             exit /b
        )
    )
    
    echo [INFO] Ollama installed. 
    echo [IMPORTANT] Please RESTART this script (close and reopen) to update system PATH.
    pause
    exit /b
)

:: 5. Model Selection & Setup
echo [5/6] Model Selection
echo ---------------------------------------------------
echo Select your preferred AI Model:
echo 1. Qwen 2.5 (7B)    - [Standard] Recommended for 8GB+ RAM/VRAM
echo 2. Qwen 2.5 (14B)   - [Advanced] Recommended for 16GB+ RAM/VRAM
echo 3. DeepSeek R1 (7B) - [Reasoning] Good logic, 8GB+ RAM/VRAM
echo 4. DeepSeek R1 (8B) - [Reasoning+] Stronger logic, 12GB+ RAM/VRAM
echo ---------------------------------------------------
set /p model_choice="Enter choice (1-4) [Default: 1]: "

if "%model_choice%"=="2" (
    set MODEL_NAME=qwen2.5:14b
) else if "%model_choice%"=="3" (
    set MODEL_NAME=deepseek-r1:7b
) else if "%model_choice%"=="4" (
    set MODEL_NAME=deepseek-r1:8b
) else (
    set MODEL_NAME=qwen2.5:7b
)

echo [INFO] Selected Model: !MODEL_NAME!

:: Check if Ollama service is responsive
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Ollama service is not running. Starting background service...
    start /B ollama serve
    echo [INFO] Waiting for Ollama to initialize...
    timeout /t 10 >nul
)

:: Check for model
ollama list | findstr "!MODEL_NAME!" >nul
if %errorlevel% neq 0 (
    echo [INFO] Model !MODEL_NAME! not found. Downloading...
    echo [INFO] This process depends on your internet speed. Please wait...
    ollama pull !MODEL_NAME!
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to pull model. Please check your internet connection.
        pause
        exit /b
    )
) else (
    echo [INFO] Model !MODEL_NAME! is ready.
)

:: 6. Start Server
echo [6/6] Starting FindUrCite Server...
echo [INFO] Server will run at http://localhost:8000
echo [INFO] Press Ctrl+C to stop the server.

start http://localhost:8000
python src/server.py

pause
