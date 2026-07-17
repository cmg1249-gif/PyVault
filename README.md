# Password Manager

A Tkinter GUI password manager built during Day 29–30 of *100 Days of Code*.

## Features

- **Generate** a strong random password (letters, numbers, symbols, shuffled) —
  automatically copied to your clipboard
- **Add** a website / email / password combo to a local `data.json`
  (not tracked in git)
- **Search** for a saved website and pop up its email and password
- Validates that all fields are filled before saving

## How to run it

The only thing you need installed is **Python** — if it's missing, the launcher
will show you exactly how to get it. Everything else installs automatically.

### Windows

1. Download this folder.
2. Double-click **`run.bat`**.
3. Follow any instructions in the black window. The app opens by itself.

### Mac / Linux

1. Download this folder.
2. Open a terminal in this folder
   (Mac: right-click the folder in Finder → *New Terminal at Folder*).
3. Type this and press Enter:

   ```
   bash run.sh
   ```

4. Follow any instructions it prints. The app opens by itself.

## Where are my passwords stored?

In `data.json`, in this folder, in plain text (encryption is planned).
Keep that file private — never share it or commit it to a public repository.
