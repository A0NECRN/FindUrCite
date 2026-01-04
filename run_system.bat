@echo off
echo ==========================================
echo       FindUrCite - AI Research Tool
echo ==========================================

REM Check if Python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

REM Check if Ollama is running
tasklist | find /i "ollama.exe" > nul
if %errorlevel% neq 0 (
    echo Starting Ollama...
    start /B ollama serve
    timeout /t 5 > nul
)

REM Check for model
echo Checking for AI Model (qwen2.5:7b)...
ollama list | findstr "qwen2.5:7b" > nul
if %errorlevel% neq 0 (
    echo Model not found. Pulling qwen2.5:7b...
    echo This may take a while depending on your internet connection.
    ollama pull qwen2.5:7b
)

REM Get User Input
set /p UserInput="Enter your research topic/viewpoint: "

REM Run Main Script
echo.
echo Running analysis...
python src/main.py "%UserInput%"

echo.
echo Done! Check research_result.md
pause
