@echo off
title ProjectLEX — Starting All Services...
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║         ProjectLEX — Starting Services          ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  Starting n8n...
start "ProjectLEX — n8n" cmd /k "title ProjectLEX ^— n8n && n8n start"

echo  Waiting for n8n to initialize...
timeout /t 5 /nobreak >nul

echo  Starting Ollama...
start "ProjectLEX — Ollama" cmd /k "title ProjectLEX ^— Ollama && ollama serve"

echo  Waiting for Ollama to initialize...
timeout /t 3 /nobreak >nul

echo  Starting File Watcher...
start "ProjectLEX — Watcher" cmd /k "title ProjectLEX ^— File Watcher && cd /d C:\Users\Loisky03\Documents\ProjectLEX && python watch_and_sync.py"

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   All services started successfully!            ║
echo  ║                                                  ║
echo  ║   n8n:      http://localhost:5678               ║
echo  ║   Ollama:   http://localhost:11434              ║
echo  ║   Watcher:  watching ProjectLEX folder          ║
echo  ║                                                  ║
echo  ║   You can close this window now.                ║
echo  ╚══════════════════════════════════════════════════╝
echo.
pause
