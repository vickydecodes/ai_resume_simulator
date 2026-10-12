#!/usr/bin/env bash

# ========================================================
#         HireFit AI - Development Runner Script
# ========================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "========================================================"
echo "        HireFit AI - Development Runner"
echo "========================================================"
echo ""

# 1. Check Python Virtual Environment (venv)
echo "[1/3] Checking Python Virtual Environment (venv)..."
VENV_PATH=""
if [ -d "$BACKEND_DIR/venv" ]; then
    echo "  [OK] Virtual environment found at backend/venv"
    VENV_PATH="$BACKEND_DIR/venv"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo "  [OK] Virtual environment found at root venv"
    VENV_PATH="$SCRIPT_DIR/venv"
else
    echo "  [MISSING] Virtual environment not found!"
    echo "  Creating virtual environment in backend/venv..."
    if command -v python3 >/dev/null 2>&1; then
        python3 -m venv "$BACKEND_DIR/venv"
    else
        python -m venv "$BACKEND_DIR/venv"
    fi
    VENV_PATH="$BACKEND_DIR/venv"
fi

# Verify dependencies (e.g. uvicorn, fastapi) are installed inside venv
echo "  Verifying backend dependencies inside venv..."
if [ -f "$VENV_PATH/Scripts/python.exe" ]; then
    PYTHON_BIN="$VENV_PATH/Scripts/python.exe"
elif [ -f "$VENV_PATH/bin/python" ]; then
    PYTHON_BIN="$VENV_PATH/bin/python"
else
    PYTHON_BIN="python"
fi

if ! "$PYTHON_BIN" -c "import uvicorn, fastapi" >/dev/null 2>&1; then
    echo "  [MISSING] Required backend packages (uvicorn/fastapi) missing in venv."
    echo "  Installing dependencies from backend/requirements.txt..."
    if [ -f "$VENV_PATH/Scripts/activate" ]; then
        source "$VENV_PATH/Scripts/activate"
    elif [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
    fi
    pip install -r "$BACKEND_DIR/requirements.txt"
    echo "  [OK] Backend dependencies installed successfully."
else
    echo "  [OK] Backend dependencies verified."
fi

# Check backend .env configuration
if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "  [INFO] Creating backend/.env from .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

# 2. Check Frontend node_modules
echo ""
echo "[2/3] Checking Frontend node_modules..."
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo "  [OK] node_modules found in frontend/"
else
    echo "  [MISSING] frontend/node_modules not found!"
    echo "  Installing frontend dependencies via npm install..."
    (cd "$FRONTEND_DIR" && npm install)
    echo "  [OK] Frontend dependencies installed successfully."
fi

# 3. Launch Backend and Frontend in separate cmd terminals
echo ""
echo "[3/3] Launching Backend and Frontend in separate cmd terminals..."

# On Windows / Git Bash / MSYS / WSL with cmd.exe available
if command -v cmd.exe >/dev/null 2>&1; then
    echo "  Launching Windows cmd terminals..."

    # Convert paths to Windows format
    if command -v cygpath >/dev/null 2>&1; then
        WIN_BACKEND_DIR="$(cygpath -w "$BACKEND_DIR")"
        WIN_FRONTEND_DIR="$(cygpath -w "$FRONTEND_DIR")"
        WIN_ACTIVATE="$(cygpath -w "$VENV_PATH/Scripts/activate.bat")"
    elif command -v wslpath >/dev/null 2>&1; then
        WIN_BACKEND_DIR="$(wslpath -w "$BACKEND_DIR")"
        WIN_FRONTEND_DIR="$(wslpath -w "$FRONTEND_DIR")"
        WIN_ACTIVATE="$(wslpath -w "$VENV_PATH/Scripts/activate.bat")"
    else
        WIN_BACKEND_DIR="$BACKEND_DIR"
        WIN_FRONTEND_DIR="$FRONTEND_DIR"
        WIN_ACTIVATE="$VENV_PATH/Scripts/activate.bat"
    fi

    CMD_BACKEND="cd /d \"$WIN_BACKEND_DIR\" && echo ======================================== && echo       HireFit AI - FastAPI Backend && echo ======================================== && call \"$WIN_ACTIVATE\" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
    CMD_FRONTEND="cd /d \"$WIN_FRONTEND_DIR\" && echo ======================================== && echo       HireFit AI - Vite Frontend && echo ======================================== && npm run dev"

    cmd.exe /c start "HireFit AI - Backend Server (FastAPI)" cmd.exe /k "$CMD_BACKEND"
    cmd.exe /c start "HireFit AI - Frontend Client (Vite)" cmd.exe /k "$CMD_FRONTEND"
else
    # Fallback if running on Linux without cmd.exe
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="HireFit AI - Backend" -- bash -c "cd '$BACKEND_DIR' && source '$VENV_PATH/bin/activate' && uvicorn app.main:app --reload --port 8000; exec bash"
        gnome-terminal --title="HireFit AI - Frontend" -- bash -c "cd '$FRONTEND_DIR' && npm run dev; exec bash"
    elif command -v x-terminal-emulator >/dev/null 2>&1; then
        x-terminal-emulator -e bash -c "cd '$BACKEND_DIR' && source '$VENV_PATH/bin/activate' && uvicorn app.main:app --reload --port 8000; exec bash" &
        x-terminal-emulator -e bash -c "cd '$FRONTEND_DIR' && npm run dev; exec bash" &
    else
        echo "  [NOTE] Starting processes in background..."
        (cd "$BACKEND_DIR" && source "$VENV_PATH/bin/activate" && uvicorn app.main:app --reload --port 8000) &
        (cd "$FRONTEND_DIR" && npm run dev) &
    fi
fi

echo ""
echo "========================================================"
echo "  Services launched in separate cmd terminal windows!"
echo "  - Backend API:  http://127.0.0.1:8000 (Swagger: /docs)"
echo "  - Frontend App: http://localhost:5173"
echo "========================================================"
echo ""
