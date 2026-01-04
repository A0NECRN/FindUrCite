@echo off
REM Switch to the script's directory (tests/)
cd /d %~dp0

echo ==========================================
echo Running FindUrCite Test Suite
echo Input: sample_draft.txt
echo ==========================================

REM Check if input file exists
if not exist "sample_draft.txt" (
    echo Error: sample_draft.txt not found in tests folder.
    pause
    exit /b 1
)

REM Run the main script
REM We use ..\src\main.py to access the source code
REM The output will be generated in the current directory (tests/)
python ..\src\main.py sample_draft.txt

echo.
echo Test completed. Check the generated research_output folder in this directory.
pause
