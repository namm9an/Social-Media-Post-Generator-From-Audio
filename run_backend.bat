@echo off
echo ======================================
echo Starting AI Social Media Post Generator Backend
echo Using D:\PythonPackages for dependencies
echo ======================================

REM Set Python path to include D:\PythonPackages
set PYTHONPATH=D:\PythonPackages\lib;%PYTHONPATH%

REM Set environment variables for model caching
set TRANSFORMERS_CACHE=D:\PythonPackages\models_cache
set TORCH_HOME=D:\PythonPackages\models_cache
set XDG_CACHE_HOME=D:\PythonPackages\models_cache

echo.
echo Starting Flask backend server...
echo Backend will be available at: http://localhost:5000
echo.

cd backend
python app.py
