@echo off
REM Run tests for wxGTD
REM This batch file activates the virtual environment and runs tests

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running tests...
python run_tests.py %*

echo.
echo Tests complete.
pause
