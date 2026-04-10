@echo off
:: ═══════════════════════════════════════════════
::  CmdBot Launcher
::  Activates venv and runs the agent globally
:: ═══════════════════════════════════════════════

:: 📁 Path to your cmdbot project folder
set PROJECT_PATH=C:\Users\aadit\Desktop\projects\CMD-Bot

:: 🐍 Activate the virtual environment
call conda activate "%PROJECT_PATH%\venv"

:: 🚀 Launch CmdBot
python "%PROJECT_PATH%\cmdbot.py"

:: 🔒 Deactivate venv cleanly after exit
call conda deactivate