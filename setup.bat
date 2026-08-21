@echo off
setlocal
title MedNexus - First Time Setup

echo ==========================================
echo        MedNexus - First Time Setup
echo ==========================================
echo.

echo [1/5] Checking Python 3.12...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 was not found.
    echo Install Python 3.12 and try again.
    pause
    exit /b 1
)
py -3.12 --version
echo.

echo [2/5] Checking Node.js and npm...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js was not found.
    echo Install Node.js LTS and try again.
    pause
    exit /b 1
)
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm was not found.
    echo Install Node.js LTS and try again.
    pause
    exit /b 1
)
node --version
npm --version
echo.

echo [3/5] Creating Python virtual environment...
if not exist "backend\venv\Scripts\python.exe" (
    py -3.12 -m venv "backend\venv"
    if errorlevel 1 (
        echo ERROR: Could not create the Python virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Existing backend\venv found - keeping it.
)
echo.

echo [4/5] Installing Python dependencies...
call "backend\venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Could not upgrade pip.
    pause
    exit /b 1
)
call "backend\venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
if errorlevel 1 (
    echo ERROR: Could not install backend dependencies.
    pause
    exit /b 1
)
echo.

echo [5/5] Installing frontend dependencies...
pushd "frontend"
call npm install
set "NPM_EXIT=%errorlevel%"
popd
if not "%NPM_EXIT%"=="0" (
    echo ERROR: npm install failed.
    pause
    exit /b %NPM_EXIT%
)

echo.
echo ==========================================
echo        MedNexus setup complete!
echo ==========================================
echo.
echo PostgreSQL must be installed and running.
echo The database/user in backend\.env must exist.
echo If needed, use backend\schema.sql to create the tables.
echo.
echo Next time, run start.bat.
echo.
pause
endlocal
