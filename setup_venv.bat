@echo off
REM Windows batch file to set up the virtual environment
echo Setting up wxGTD virtual environment...
python setup_venv.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
    echo.
    echo To activate the virtual environment, run:
    echo   venv\Scripts\activate
    echo.
) else (
    echo.
    echo Setup failed! Please check the error messages above.
    echo.
)
pause
