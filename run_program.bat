@echo off
REM Run wxGTD program in the virtual environment
call venv\Scripts\activate.bat
python wxgtd.pyw %*
pause
