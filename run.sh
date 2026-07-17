#!/usr/bin/env bash
# Launcher for Mac and Linux.
# To run it: open a terminal in this folder and type:  bash run.sh
set -e
cd "$(dirname "$0")"

# Find a Python 3 interpreter
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "============================================================"
    echo " Python is not installed on this computer (it's required)."
    echo ""
    echo " How to fix it - step by step:"
    echo ""
    echo " On a Mac:"
    echo "   1. Open this link in your web browser:"
    echo "        https://www.python.org/downloads/"
    echo "   2. Click the big yellow 'Download Python' button."
    echo "   3. Open the downloaded file and click through the installer."
    echo "   4. Run this launcher again:  bash run.sh"
    echo ""
    echo " On Linux, install it with your package manager:"
    echo "   Ubuntu/Debian:  sudo apt install python3"
    echo "   Arch:           sudo pacman -S python"
    echo "   Then run this launcher again:  bash run.sh"
    echo "============================================================"
    exit 1
fi

# Make sure tkinter is available (some Linux distros package it separately)
if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo "============================================================"
    echo " Python is installed, but 'tkinter' (the part that draws"
    echo " the app's window) is missing."
    echo ""
    echo " How to fix it - copy and run ONE of these commands:"
    echo "   Ubuntu/Debian:  sudo apt install python3-tk"
    echo "   Fedora:         sudo dnf install python3-tkinter"
    echo "   Arch:           sudo pacman -S tk"
    echo ""
    echo " Then run this launcher again:  bash run.sh"
    echo "============================================================"
    exit 1
fi

# Make sure pip is available
if ! "$PY" -m pip --version >/dev/null 2>&1; then
    echo "pip (Python's package installer) is missing - installing it now."
    echo "This is automatic, you don't need to do anything..."
    "$PY" -m ensurepip --upgrade
fi

echo ""
echo "Step 1 of 2: Installing the packages this app needs..."
echo "(This is automatic and only slow the first time.)"
if ! "$PY" -m pip install --user -r requirements.txt; then
    echo "============================================================"
    echo " Something went wrong installing the packages."
    echo " Check your internet connection, then try again with:"
    echo "   bash run.sh"
    echo "============================================================"
    exit 1
fi

# The app stores its encryption key in the OS keyring; on Linux that needs
# a Secret Service daemon (GNOME Keyring or KWallet). Warn if none is running.
if [ "$(uname)" = "Linux" ] && ! pgrep -x gnome-keyring-daemon >/dev/null 2>&1 && ! pgrep -f kwalletd >/dev/null 2>&1; then
    echo ""
    echo "Note: no keyring service (GNOME Keyring / KWallet) appears to be running."
    echo "The app needs one to store its encryption key. On a minimal setup, install"
    echo "and start one, e.g.:"
    echo "  Ubuntu/Debian:  sudo apt install gnome-keyring"
    echo "  Arch:           sudo pacman -S gnome-keyring"
    echo "Desktop environments like GNOME or KDE usually have this already."
fi

# pyperclip on Linux needs a clipboard helper
if [ "$(uname)" = "Linux" ] && ! command -v xclip >/dev/null 2>&1 && ! command -v xsel >/dev/null 2>&1 && ! command -v wl-copy >/dev/null 2>&1; then
    echo ""
    echo "Note: the app will still work, but the copy-to-clipboard button"
    echo "needs one extra tool. To enable it, run ONE of these:"
    echo "  Ubuntu/Debian:  sudo apt install xclip"
    echo "  Arch:           sudo pacman -S xclip"
fi

echo ""
echo "Step 2 of 2: Starting the Password Manager..."
echo "(A new window should open. Keep this terminal open while you use it.)"
"$PY" main.py

echo ""
echo "The Password Manager has closed."
