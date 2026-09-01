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
python -c "import pyperclip, cryptography, keyring, requests, argon2" >nul 2>nul
if errorlevel 1 goto setup

goto launch


REM ===========================================================
REM  SETUP - only runs the first time, or after something changes
REM ===========================================================
:setup
echo.
echo  Setting up PyVault. This only happens once.
echo.

REM  Actually RUN python rather than just looking for the file. Windows
REM  ships "app execution alias" stubs at
REM    %LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
REM  on machines with no Python at all - they exist only to open the
REM  Microsoft Store. "where python" finds those and reports success, so
REM  it cannot tell "installed" from "not installed". The same stubs can
REM  also be left dangling after a Store update, pointing at a package
REM  version that is no longer there. Running python is the only check
REM  that catches every case.
python -c "import sys" >nul 2>nul
if errorlevel 1 (
    echo ============================================================
    echo  Python is not installed on this computer ^(it's required^).
    echo.
    echo  How to fix it - step by step:
    echo    1. Open the Microsoft Store
    echo       ^(click Start, type "Microsoft Store", press Enter^).
    echo    2. Search for:  Python
    echo    3. Pick the newest version published by the
    echo       "Python Software Foundation" and click Get / Install.
    echo    4. Wait for it to finish installing.
    echo    5. Close this window and double-click run.bat again.
    echo.
    echo  No Microsoft Store? You can install from python.org instead:
    echo         https://www.python.org/downloads/
    echo    On the FIRST install screen, tick the checkbox that says
    echo    "Add Python to PATH" ^(near the bottom^), then Install Now.
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
REM  Ask the script itself, because a shortcut file existing is not the same
REM  as it working - after re-installing to a new folder the old one is still
REM  sat on the Desktop pointing at a folder that has gone.
powershell -NoProfile -ExecutionPolicy Bypass -File "%APPDIR%make_shortcut.ps1" -CheckOnly
if not errorlevel 1 (
    echo  You already have one pointing here - leaving it alone.
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
