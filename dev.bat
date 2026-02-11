@echo off
echo ==========================================
echo   WebSH Development Server Starter
echo ==========================================

:: 1. Start Python Kernel in a new window
echo [1/2] Starting Kernel (Backend)...
start "WebSH Kernel" cmd /k "venv\Scripts\activate && python main.py"

:: 2. Start Svelte Shell in the current window (or new if preferred, but keep it here to see logs)
echo [2/2] Starting Shell (Frontend)...
cd shell
npm run dev -- --open
