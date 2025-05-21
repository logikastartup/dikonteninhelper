@echo off
setlocal enabledelayedexpansion

REM Check if Python 3.12 is installed
python --version 2>nul | findstr /r "^Python 3\.12\." >nul
if errorlevel 1 (
    echo Python 3.12 is not installed. Opening download page...
    start "" "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
    echo Please install Python 3.12 and run this script again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install requirements
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if requirements are installed
if exist "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting DikontenIn Helper...
python main_gui.py

REM Deactivate virtual environment at the end
call deactivate
exit /b 0
