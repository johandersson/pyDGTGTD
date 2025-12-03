@echo off
REM Run tests for wxGTD
REM This batch file runs tests, checking for virtual environment

if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, running with system Python...
)

echo.
echo Running tests...
python run_tests.py %*

echo.
echo Tests complete.
pause
