@echo off
setlocal

title MedNexus

cd /d "%~dp0"

echo ==========================================
echo          Starting MedNexus
echo ==========================================
echo.

REM ------------------------------------------
REM Check backend virtual environment
REM ------------------------------------------
if not exist "backend\venv\Scripts\python.exe" (
    echo ERROR: Backend virtual environment not found.
    echo.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------
REM Check frontend dependencies
REM ------------------------------------------
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not found.
    echo.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting backend...
start "MedNexus Backend" cmd /k "cd /d ""%~dp0"" && backend\venv\Scripts\python.exe backend\run.py"

timeout /t 3 /nobreak >nul

echo Starting frontend...
start "MedNexus Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

timeout /t 5 /nobreak >nul

echo Opening MedNexus...
start "" "http://localhost:5173"

echo.
echo ==========================================
echo        MedNexus is starting!
echo ==========================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:5000
echo.
echo Keep the two terminal windows open.
echo Close them to stop MedNexus.
echo.

exit /b 0