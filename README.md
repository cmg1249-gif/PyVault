# PyVault

A Tkinter GUI password manager with an encrypted vault. Started as Day 29–30 of
*100 Days of Code*, then extended with real encryption, OS-keyring key storage,
and an account browser.

> **⚠️ Educational project — please read before trusting it with real passwords.**
> I built PyVault to learn cryptography, GUI development, and software release
> practices. It uses real encryption (Fernet via the `cryptography` library),
> but it has **not been security-audited**, and it has known gaps a mature
> password manager doesn't (passwords shown in plaintext popups, clipboard is
> never cleared). For accounts you actually care about, use an established
> password manager. Provided as-is, without warranty — see [LICENSE](LICENSE).

## Features

- **Generate** a strong random password (letters, numbers, symbols, shuffled) —
  automatically copied to your clipboard
- **Add** a website / email / password combo to the encrypted vault
- **Search** for a saved website and pop up its email and password
- **All Accounts** view — every saved website and email in one selectable,
  copyable window (passwords stay hidden; search to reveal one)
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

In an **encrypted vault file** in this folder, encrypted with
[Fernet](https://cryptography.io/en/latest/fernet/) (AES-128-CBC + HMAC).
The encryption key is stored in your **operating system's keyring**
(Windows Credential Manager / macOS Keychain / Linux Secret Service), not in
the file and not in the code.

Two things to know:

- **Don't delete the PyVault entry in your OS's credential/key manager.**
  Without the key, the vault cannot be decrypted and your saved passwords are
  gone for good.
- **There is no cloud backup.** Everything lives on this machine. If the
  machine or OS user account is lost, so is the vault. (Key export/backup is
  planned.)

## Version history

See [CHANGELOG.md](CHANGELOG.md). Current release: **v1.2.0**.

## License

[MIT](LICENSE)
