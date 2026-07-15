#!/usr/bin/env bash
# Launcher for Mac and Linux
set -e
cd "$(dirname "$0")"

# Find a Python 3 interpreter
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "Python was not found on this computer."
    echo "Mac:   install from https://www.python.org/downloads/ or 'brew install python'"
    echo "Linux: install with your package manager, e.g. 'sudo apt install python3'"
    exit 1
fi

# Make sure tkinter is available (some Linux distros package it separately)
if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo "Python is installed but tkinter is missing."
    echo "Linux: install it with e.g. 'sudo apt install python3-tk' (Debian/Ubuntu)"
    echo "       or 'sudo pacman -S tk' (Arch)"
    exit 1
fi

# Make sure pip is available
if ! "$PY" -m pip --version >/dev/null 2>&1; then
    echo "pip was not found, installing it now..."
    "$PY" -m ensurepip --upgrade
fi

echo "Installing required packages..."
"$PY" -m pip install --user -r requirements.txt

# pyperclip on Linux needs a clipboard helper
if [ "$(uname)" = "Linux" ] && ! command -v xclip >/dev/null 2>&1 && ! command -v xsel >/dev/null 2>&1 && ! command -v wl-copy >/dev/null 2>&1; then
    echo "Note: for the copy-to-clipboard feature on Linux, install xclip:"
    echo "      e.g. 'sudo apt install xclip' or 'sudo pacman -S xclip'"
fi

echo "Starting Password Manager..."
"$PY" main.py
