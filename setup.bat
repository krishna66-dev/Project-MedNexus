@echo off
setlocal

title MedNexus Setup

cd /d "%~dp0"

echo ==========================================
echo        MedNexus - Project Setup
echo ==========================================
echo.

REM ------------------------------------------
REM Check Python
REM ------------------------------------------
echo [1/4] Checking Python...

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Please install Python 3.12 or newer.
    pause
    exit /b 1
)

py --version
echo.

REM ------------------------------------------
REM Create Python virtual environment
REM ------------------------------------------
echo [2/4] Setting up Python virtual environment...

if not exist "backend\venv\Scripts\python.exe" (
    echo Creating backend virtual environment...

    py -3.12 -m venv backend\venv

    if errorlevel 1 (
        echo Python 3.12 was not found.
        echo Trying the default Python installation...
        py -m venv backend\venv
    )
) else (
    echo Existing virtual environment found.
)

echo.

REM ------------------------------------------
REM Install backend dependencies
REM ------------------------------------------
echo Installing backend dependencies...

backend\venv\Scripts\python.exe -m pip install --upgrade pip

if errorlevel 1 (
    echo ERROR: Could not upgrade pip.
    pause
    exit /b 1
)

backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt

if errorlevel 1 (
    echo ERROR: Backend dependencies could not be installed.
    pause
    exit /b 1
)

echo.

REM ------------------------------------------
REM Check Node.js
REM ------------------------------------------
echo [3/4] Checking Node.js...

where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed.
    echo Please install Node.js LTS.
    pause
    exit /b 1
)

node --version
npm --version
echo.

REM ------------------------------------------
REM Install frontend dependencies
REM ------------------------------------------
echo [4/4] Installing frontend dependencies...

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm packages...
    npm install
) else (
    echo node_modules already exists.
    echo Checking npm packages...
    npm install
)

if errorlevel 1 (
    echo ERROR: Frontend dependencies could not be installed.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo.
echo ==========================================
echo       MedNexus Setup Complete!
echo ==========================================
echo.
echo You can now run:
echo.
echo     start.bat
echo.
echo This will start both the backend and frontend.
echo.
pause