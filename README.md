# PyVault

A Tkinter GUI password manager with an encrypted vault. Started as Day 29–30 of
*100 Days of Code*, then extended with real encryption, OS-keyring key storage,
breach checking, key and vault backup, and an account browser.

> **⚠️ Educational project — please read before trusting it with real passwords.**
> I built PyVault to learn cryptography, GUI development, and software release
> practices. It uses real encryption (Fernet via the `cryptography` library),
> but it has **not been security-audited**, and it has known gaps a mature
> password manager doesn't:
>
> - **No master password.** PyVault unlocks the vault automatically using the
>   key in your OS keyring. Anyone who can use your unlocked computer can open
>   PyVault and read every saved password.
> - Passwords are shown in plaintext popups.
> - Clipboard auto-clear can't scrub Windows clipboard *history* (Win+V), and
>   won't fire if the app is closed mid-countdown.
>
> For accounts you actually care about, use an established password manager.
> Provided as-is, without warranty — see [LICENSE](LICENSE).

## Features

- **Generate** a strong 13-character password using Python's `secrets` module
  (cryptographically secure randomness — letters, digits, and symbols,
  securely shuffled) — automatically copied to your clipboard
- **Clipboard auto-clear** — generated passwords are wiped from the clipboard
  after 10 seconds (only if the clipboard still holds the password, so
  anything you copied in the meantime is left alone)
- **Breach check on save (PwnCheck)** — passwords are checked against the
  Have I Been Pwned database before saving. Uses k-anonymity: only the first
  5 characters of the password's SHA-1 hash are ever sent, and the password
  itself never leaves your machine. If the service is unreachable, saving
  proceeds normally
- **Add** a website / email / password combo to the encrypted vault
- **Overwrite warning** — saving a website you already have an entry for asks
  before replacing it, so an existing password is never silently clobbered
- **Search** for a saved website and pop up its email and password
- **All Accounts** view — every saved website and email in one window.
  **Double-click any row** to reveal that account's password without retyping
  the website into Search. Opens as a single window: clicking the button again
  brings it to the front instead of spawning duplicates, and the list refreshes
  itself after you save so it never shows stale entries
- **Delete accounts** from the All Accounts window — select an entry,
  confirm, and it's removed from the encrypted vault
- **Key backup and restore** — *Options → Export Vault Key* writes your
  encryption key to a file you choose; *Import Vault Key* restores it.
  Imports are validated before they commit
- **Vault backup and restore** — *Options → Export Vault* saves a copy of your
  encrypted vault; *Import Vault* replaces it from a backup. Importing copies
  the current vault to `data.enc.bak` first, and warns if your key doesn't open
  the vault you're bringing in
- Validates that all fields are filled before saving

## How to run it

The only thing you need installed is **Python** — if it's missing, the launcher
will show you exactly how to get it. Everything else installs automatically.

### Windows

1. **Install Python from the Microsoft Store** — click Start, type
   *Microsoft Store*, press Enter, search for **Python**, and install the
   newest version published by the *Python Software Foundation*. This is the
   easiest route: it sets everything up for you, with no PATH checkbox to
   remember. (Prefer python.org? That works too — just tick **Add Python to
   PATH** on the first install screen.)
2. Download this folder.
3. Double-click **`run.bat`**.
4. The first launch installs what it needs and offers to put a **PyVault
   shortcut on your Desktop**. Follow anything it says in the black window.

If Python is missing, `run.bat` stops and walks you through installing it —
it won't leave you guessing.

After that first run, open PyVault from the Desktop shortcut. It starts
straight into the app with **no black window at all** — the setup steps only
repeat if the required packages change.

Don't want the shortcut, or need to recreate it later? Right-click
**`make_shortcut.ps1`** and choose *Run with PowerShell*. It also repairs a
shortcut left pointing at an older PyVault folder.

### Mac / Linux

1. Download this folder.
2. Open a terminal in this folder
   (Mac: right-click the folder in Finder → *New Terminal at Folder*).
3. Type this and press Enter:

   ```
   bash run.sh
   ```

4. Follow any instructions it prints. The app opens by itself.

On Mac and Linux the terminal window needs to stay open while you use the app,
and there's no Desktop shortcut — those are Windows-only for now.

## Where are my passwords stored?

In an **encrypted vault file** at `~/PyVault_Vault/data.enc` — your home
folder, deliberately *not* the program folder, so updating or re-downloading
PyVault never disturbs it. It's encrypted with
[Fernet](https://cryptography.io/en/latest/fernet/) (AES-128-CBC + HMAC).

The encryption key is stored in your **operating system's keyring**
(Windows Credential Manager / macOS Keychain / Linux Secret Service), not in
the vault file and not in the code.

That split is the whole design: **the vault file is useless without the key,
and the key is useless without the vault file.**

## Backing up

You need **both** pieces to restore, and they're backed up separately.

**Your key** — *Options → Export Vault Key*, and keep the file somewhere safe.
Do this now, before you need it. Without the key, a vault file is
unrecoverable; there is no reset, no recovery email, and no way around it.

**Your vault** — *Options → Export Vault* writes a copy wherever you choose (or
copy `~/PyVault_Vault/data.enc` yourself). It's just ciphertext, so it's the
safe half to keep in cloud storage.

### Store them in different places

Anyone holding both files has all of your passwords, so putting them together
undoes the encryption entirely. Keep them apart — key on a USB stick in a
drawer, vault in cloud storage, or any similar split.

The upside of that split: **a vault file on its own is safe to store almost
anywhere**, because it's just ciphertext. The key file is the sensitive one.
Treat it exactly as carefully as the passwords it protects.

### Restoring on a new machine

1. Install PyVault and run it once.
2. *Options → Import Vault Key*, and pick your key backup.
3. *Options → Import Vault*, and pick your vault backup (or copy `data.enc`
   back to `~/PyVault_Vault/` yourself).

Importing the key first means the vault opens as soon as it lands. If you do it
the other way round, PyVault imports the vault but warns that your key won't
open it yet — bring the key across next and you're set.

If a vault ever won't open, the cause is almost always a key that doesn't match
it. **Your passwords are still there** — the file is locked, not damaged.
Import the right key rather than resetting the vault.

## Version history

See [CHANGELOG.md](CHANGELOG.md). Current release: **v1.9.0**.

## License

[MIT](LICENSE)
