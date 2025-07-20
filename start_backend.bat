@echo off
echo ======================================
echo Starting AI Social Media Post Generator Backend
echo ======================================

cd /d "D:\Academics\projects\Social Media Post Generator from Audio\backend"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set Python path to include current directory
set PYTHONPATH=.;%PYTHONPATH%

echo.
echo Starting Flask backend server...
echo Backend will be available at: http://localhost:5000
echo.

python app.py

pause
