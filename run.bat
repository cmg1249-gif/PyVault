@echo off
setlocal EnableExtensions
title PyVault Launcher

set "APPDIR=%~dp0"
set "MARKER=%APPDIR%.setup_complete"
cd /d "%APPDIR%"

REM ===========================================================
REM  FAST PATH
REM  Once setup has run and nothing has changed, we start the app
REM  with pythonw (which has no console window) and this window
REM  closes straight away.
REM ===========================================================
if not exist "%MARKER%" goto setup

REM  .setup_complete holds the hash of the package list from the last
REM  successful setup. A different hash means requirements.txt was
REM  edited, so the new packages need installing.
set "REQHASH="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "requirements.txt" MD5 2^>nul') do (
    if not defined REQHASH set "REQHASH=%%H"
)
set /p SAVEDHASH=<"%MARKER%"
if not "%REQHASH%"=="%SAVEDHASH%" goto setup

REM  Cheap safety net: if a package has been removed or the Python
REM  install has changed, drop back into the visible setup.
REM  Keep this list in step with requirements.txt.
python -c "import pyperclip, cryptography, keyring, requests" >nul 2>nul
if errorlevel 1 goto setup

goto launch


REM ===========================================================
REM  SETUP - only runs the first time, or after something changes
REM ===========================================================
:setup
echo.
echo  Setting up PyVault. This only happens once.
echo.

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

echo  Step 1 of 2: Installing the packages this app needs...
echo  ^(This is automatic and only slow the first time.^)
python -m pip install -r "%APPDIR%requirements.txt"
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
echo  Step 2 of 2: Setting up your Desktop shortcut...
if exist "%USERPROFILE%\Desktop\PyVault.lnk" (
    echo  You already have one - leaving it alone.
) else (
    REM  /t 15 /d Y means an unattended run carries on by itself.
    choice /c YN /n /t 15 /d Y /m "  Put a PyVault shortcut on your Desktop? [Y/n] "
    if not errorlevel 2 (
        powershell -NoProfile -ExecutionPolicy Bypass -File "%APPDIR%make_shortcut.ps1" -Quiet
        if errorlevel 1 echo  Could not create the shortcut - you can still use run.bat.
    )
)

REM  Record the package list we just installed, so the next launch can
REM  skip all of the above and go straight to the app.
set "REQHASH="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "requirements.txt" MD5 2^>nul') do (
    if not defined REQHASH set "REQHASH=%%H"
)
>"%MARKER%" echo %REQHASH%

echo.
echo  Setup is done. From now on PyVault opens straight away,
echo  with no black window.
echo.


REM ===========================================================
REM  LAUNCH
REM ===========================================================
:launch
REM  pythonw runs the app without a console attached. start lets this
REM  script exit immediately instead of waiting for the app to close.
start "" pythonw "%APPDIR%main.py"
exit /b 0
