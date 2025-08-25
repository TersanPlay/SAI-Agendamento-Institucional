@echo off
REM Script to activate virtual environment with clean environment variables
REM This helps avoid conflicts with globally installed Python packages

REM Clear PYTHONPATH to avoid conflicts with global installations
set PYTHONPATH=

REM Clear any existing Django settings that might conflict
set DJANGO_SETTINGS_MODULE=

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Display confirmation
echo Virtual environment activated with clean environment variables
echo Python version:
python --version
echo Django version:
python -m django --version

echo.
echo Ready to work on EventoSys project!
echo Remember to always activate the virtual environment before working on this project
