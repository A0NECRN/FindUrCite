@echo off
cd /d %~dp0
echo ==========================================
echo Running FindUrCite Test Suite
echo Input: sample_draft.txt
echo ==========================================
if not exist "sample_draft.txt" (
    echo Error: sample_draft.txt not found in tests folder.
    pause
    exit /b 1
)
python ..\src\main.py sample_draft.txt
echo.
echo Test completed. Check the generated research_output folder in this directory.
pause
