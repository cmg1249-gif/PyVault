@echo off
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on this computer.
    echo Please install it from https://www.python.org/downloads/
    echo During install, make sure to check "Add Python to PATH".
    pause
    exit /b 1
)

python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo pip was not found, installing it now...
    python -m ensurepip --upgrade
)

echo Installing required packages...
python -m pip install -r "%~dp0requirements.txt"

echo Starting Password Manager...
cd /d "%~dp0"
python main.py

pause
