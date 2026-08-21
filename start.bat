@echo off
setlocal
title MedNexus - Start

echo ==========================================
echo          Starting MedNexus
echo ==========================================
echo.

if not exist "backend\venv\Scripts\python.exe" (
    echo ERROR: Backend virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "backend\.env" (
    echo ERROR: backend\.env not found.
    pause
    exit /b 1
)

echo Starting Flask backend...
start "MedNexus Backend" cmd /k "cd /d ""%~dp0backend"" && ""venv\Scripts\python.exe"" run.py"

timeout /t 3 /nobreak >nul

echo Starting Svelte frontend...
start "MedNexus Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:5000
echo.
echo Opening the frontend...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"
endlocal
