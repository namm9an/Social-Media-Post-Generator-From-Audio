@echo off
REM ============================================================
REM  AI Social Media Post Generator – Environment & Runner
REM  Creates Python virtualenv, installs deps, then starts back & front
REM ============================================================

setlocal

REM Change to project root (directory containing this script)
pushd %~dp0\..

REM ------------------------------------------------------------
REM 1. Python virtual environment
REM ------------------------------------------------------------
IF NOT EXIST .venv (
    echo Creating Python virtual environment in .venv ...
    python -m venv .venv || goto :error
)

call .\.venv\Scripts\activate

python -m pip install --upgrade pip

REM Install root + backend requirements
python -m pip install -r requirements.txt || goto :error
python -m pip install -r backend\requirements.txt || goto :error

REM ------------------------------------------------------------
REM 2. Node dependencies (frontend)
REM ------------------------------------------------------------
pushd frontend
if not exist node_modules (
    echo Installing React dependencies ...
    npm install || goto :error
)
popd

REM ------------------------------------------------------------
REM 3. Launch backend in new window
REM ------------------------------------------------------------
start "backend" cmd /k "cd backend && call ..\.venv\Scripts\activate && python app.py"

REM ------------------------------------------------------------
REM 4. Launch frontend in this window
REM ------------------------------------------------------------
cd frontend
npm start --no-open

:end
popd
exit /b 0

:error
echo.
echo ERROR occurred during setup.^ Verify Python/Node installations.
popd
exit /b 1
