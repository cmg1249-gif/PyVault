# Password Manager

A Tkinter GUI password manager built during Day 29–30 of *100 Days of Code*.

## Features

- Generates strong random passwords (letters, numbers, symbols, shuffled)
- Copies the generated password straight to the clipboard (`pyperclip`)
- Validates that all fields are filled before saving
- Confirmation dialog before writing
- Saves website / email / password combos to a local `data.txt` (not tracked in git)

## Run it

**Windows:** double-click `run.bat`
**Mac / Linux:** `bash run.sh`

The launcher checks for Python and pip, installs the one dependency
(`pyperclip`), and starts the app.
