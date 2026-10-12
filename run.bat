@echo off
setlocal enabledelayedexpansion
title HireFit AI - System Launcher

echo ========================================================
echo         HireFit AI - Development Runner
echo ========================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

:: 1. Check Python Virtual Environment (venv)
echo [1/3] Checking Python Virtual Environment (venv)...
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo   [OK] Virtual environment found at backend\venv
    set "VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate.bat"
    set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
) else if exist "%ROOT_DIR%venv\Scripts\activate.bat" (
    echo   [OK] Virtual environment found at root venv
    set "VENV_ACTIVATE=%ROOT_DIR%venv\Scripts\activate.bat"
    set "PYTHON_EXE=%ROOT_DIR%venv\Scripts\python.exe"
) else (
    echo   [MISSING] Virtual environment not found!
    echo   Creating virtual environment in backend\venv...
    python -m venv "%BACKEND_DIR%\venv"
    if errorlevel 1 (
        echo   [ERROR] Failed to create venv. Ensure Python 3.10+ is installed and in PATH.
        pause
        exit /b 1
    )
    set "VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate.bat"
    set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
)

:: Verify dependencies (e.g. uvicorn, fastapi) are installed inside venv
echo   Verifying backend dependencies inside venv...
"%PYTHON_EXE%" -c "import uvicorn, fastapi" >nul 2>&1
if errorlevel 1 (
    echo   [MISSING] Required backend packages uvicorn and fastapi missing in venv.
    echo   Installing dependencies from backend\requirements.txt...
    call "%VENV_ACTIVATE%"
    pip install -r "%BACKEND_DIR%\requirements.txt"
    if errorlevel 1 (
        echo   [ERROR] Failed to install backend requirements.
        pause
        exit /b 1
    )
    echo   [OK] Backend dependencies installed successfully.
) else (
    echo   [OK] Backend dependencies verified.
)

:: Check backend .env configuration
if not exist "%BACKEND_DIR%\.env" (
    if exist "%BACKEND_DIR%\.env.example" (
        echo   [INFO] Creating backend\.env from .env.example...
        copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    )
)

:: 2. Check Frontend node_modules
echo.
echo [2/3] Checking Frontend node_modules...
if exist "%FRONTEND_DIR%\node_modules" (
    echo   [OK] node_modules found in frontend\
) else (
    echo   [MISSING] frontend\node_modules not found!
    echo   Installing frontend dependencies via npm install...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
    if errorlevel 1 (
        echo   [ERROR] npm install failed. Please check Node.js and npm installations.
        pause
        exit /b 1
    )
    echo   [OK] Frontend dependencies installed successfully.
)

:: 3. Launch Backend and Frontend in separate cmd terminals
echo.
echo [3/3] Launching Backend and Frontend in separate cmd terminals...

echo   Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "HireFit AI - Backend Server (FastAPI)" cmd /k "cd /d "%BACKEND_DIR%" && echo ======================================== && echo       HireFit AI - FastAPI Backend && echo ======================================== && echo Activating virtual environment... && call "%VENV_ACTIVATE%" && echo Starting Uvicorn server on http://127.0.0.1:8000... && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo   Starting Frontend (Vite on http://localhost:5173)...
start "HireFit AI - Frontend Client (Vite)" cmd /k "cd /d "%FRONTEND_DIR%" && echo ======================================== && echo       HireFit AI - Vite Frontend && echo ======================================== && echo Starting Vite development server... && npm run dev"

echo.
echo ========================================================
echo   Services launched in separate cmd terminal windows!
echo   - Backend API:  http://127.0.0.1:8000 (Swagger: /docs)
echo   - Frontend App: http://localhost:5173
echo ========================================================
echo.
