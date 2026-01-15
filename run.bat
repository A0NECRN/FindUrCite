@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: Ensure critical system paths are in PATH
set "PATH=%PATH%;%SystemRoot%\System32;%SystemRoot%\System32\WindowsPowerShell\v1.0"

title FindUrCite Launcher
cd /d "%~dp0"

echo ===================================================
echo       FindUrCite - AI Research Assistant
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
if exist "venv" goto :venv_exists
echo [INFO] Creating virtual environment...
python -m venv venv
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b
)
:venv_exists

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
if %errorlevel% equ 0 goto :ollama_installed

:: Check common install locations
set FOUND_OLLAMA=0
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo [INFO] Found Ollama in AppData. Adding to PATH...
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
    set FOUND_OLLAMA=1
)
if !FOUND_OLLAMA! equ 1 goto :ollama_installed

echo [WARN] Ollama not found in PATH.

:: Try to find PowerShell
set "PS_CMD=powershell"
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" (
        set "PS_CMD=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
    )
)

echo [INFO] Attempting to install via Winget...
winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements >nul 2>&1

:: Check if winget worked (it might not be in path or failed)
where ollama >nul 2>&1
if %errorlevel% equ 0 goto :ollama_installed

echo [WARN] Winget installation failed or not available. Attempting direct download...
echo [INFO] Downloading OllamaSetup.exe...

!PS_CMD! -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"

if not exist "OllamaSetup.exe" (
     echo [ERROR] Failed to download Ollama.
     echo [ERROR] Please install manually from https://ollama.com/
     pause
     exit /b
)

echo [INFO] Installer downloaded. Launching...
echo [INFO] Please complete the installation in the new window.
start /wait OllamaSetup.exe
del OllamaSetup.exe
goto :ollama_check_again

:ollama_check_again
echo [INFO] Checking Ollama installation again...
where ollama >nul 2>&1
if %errorlevel% equ 0 goto :ollama_installed

echo [IMPORTANT] Please RESTART this script (close and reopen) to update system PATH.
pause
exit /b

:ollama_installed
echo [INFO] Ollama is ready.

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

if "%model_choice%"=="2" goto set_qwen14
if "%model_choice%"=="3" goto set_ds7
if "%model_choice%"=="4" goto set_ds8
goto set_default

:set_qwen14
set MODEL_NAME=qwen2.5:14b
goto model_selected

:set_ds7
set MODEL_NAME=deepseek-r1:7b
goto model_selected

:set_ds8
set MODEL_NAME=deepseek-r1:8b
goto model_selected

:set_default
set MODEL_NAME=qwen2.5:7b
goto model_selected

:model_selected
echo [INFO] Selected Model: !MODEL_NAME!

:: Check if Ollama service is responsive
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Ollama service is not running. Starting background service...
    start /B ollama serve
    echo [INFO] Waiting for Ollama to initialize...
    ping 127.0.0.1 -n 11 >nul
)

:: Check for model
ollama list | %SystemRoot%\System32\findstr.exe "!MODEL_NAME!" >nul
if %errorlevel% equ 0 goto :model_ready

echo [INFO] Model !MODEL_NAME! not found. Downloading...
echo [INFO] This process depends on your internet speed. Please wait...
ollama pull !MODEL_NAME!
if !errorlevel! neq 0 (
    echo [ERROR] Failed to pull model. Please check your internet connection.
    pause
    exit /b
)

:model_ready
echo [INFO] Model !MODEL_NAME! is ready.

:: 6. Start Web App
echo [6/6] Starting FindUrCite Web App...
echo [INFO] Launching Streamlit...

streamlit run src/web_app.py --browser.gatherUsageStats false

pause
