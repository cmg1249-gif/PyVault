# PyVault

A Tkinter GUI password manager with an encrypted vault. Started as Day 29–30 of
*100 Days of Code*, then extended with real encryption, OS-keyring key storage,
and an account browser.

> **⚠️ Educational project — please read before trusting it with real passwords.**
> I built PyVault to learn cryptography, GUI development, and software release
> practices. It uses real encryption (Fernet via the `cryptography` library),
> but it has **not been security-audited**, and it has known gaps a mature
> password manager doesn't (passwords shown in plaintext popups; clipboard
> auto-clear can't scrub Windows clipboard *history* (Win+V) or clear if the
> app is closed mid-countdown; no key backup yet). For accounts you actually
> care about, use an established password manager. Provided as-is, without
> warranty — see [LICENSE](LICENSE).

## Features

- **Generate** a strong random password using Python's `secrets` module
  (cryptographically secure randomness — letters, digits, and symbols,
  securely shuffled) — automatically copied to your clipboard
- **Clipboard auto-clear** — generated passwords are wiped from the clipboard
  after 10 seconds (only if the clipboard still holds the password, so
  anything you copied in the meantime is left alone)
- **Add** a website / email / password combo to the encrypted vault
- **Search** for a saved website and pop up its email and password
- **All Accounts** view — every saved website and email in one window
  (passwords stay hidden; search to reveal one). Opens as a single window:
  clicking the button again brings it to the front instead of spawning
  duplicates
- **Delete accounts** from the All Accounts window — select an entry,
  confirm, and it's removed from the encrypted vault
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

See [CHANGELOG.md](CHANGELOG.md). Current release: **v1.4.3**.

## License

[MIT](LICENSE)
