@echo off
title Password Manager Launcher

where python >nul 2>nul
if errorlevel 1 (
    echo ============================================================
    echo  Python is not installed on this computer ^(it's required^).
    echo.
    echo  How to fix it - step by step:
    echo    1. Open this link in your web browser:
    echo         https://www.python.org/downloads/
    echo    2. Click the big yellow "Download Python" button.
    echo    3. Open the file that downloads.
    echo    4. IMPORTANT: on the first install screen, tick the
    echo       checkbox that says "Add Python to PATH"
    echo       ^(it's near the bottom of the window^).
    echo    5. Click "Install Now" and wait for it to finish.
    echo    6. Close this window and double-click run.bat again.
    echo ============================================================
    pause
    exit /b 1
)

python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo pip ^(Python's package installer^) is missing - installing it now.
    echo This is automatic, you don't need to do anything...
    python -m ensurepip --upgrade
)

echo.
echo Step 1 of 2: Installing the packages this app needs...
echo (This is automatic and only slow the first time.)
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo ============================================================
    echo  Something went wrong installing the packages.
    echo  Check your internet connection, then double-click
    echo  run.bat to try again.
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo Step 2 of 2: Starting the Password Manager...
echo (A new window should open. You can minimize this black window,
echo  but don't close it while the app is running.)
cd /d "%~dp0"
python main.py

echo.
echo The Password Manager has closed. You can close this window now.
pause
