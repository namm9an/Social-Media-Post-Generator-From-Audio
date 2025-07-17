@echo off
echo ======================================
echo AI Social Media Post Generator Setup
echo Installing to D:\PythonPackages
echo ======================================

REM Set Python path to include D:\PythonPackages
set PYTHONPATH=D:\PythonPackages\lib;%PYTHONPATH%

REM Create directories
mkdir "D:\PythonPackages\lib" 2>nul
mkdir "D:\PythonPackages\models_cache" 2>nul

REM Set environment variables for model caching
set TRANSFORMERS_CACHE=D:\PythonPackages\models_cache
set TORCH_HOME=D:\PythonPackages\models_cache
set XDG_CACHE_HOME=D:\PythonPackages\models_cache

echo.
echo Running Python setup script...
python setup.py

echo.
echo Setup complete!
pause
