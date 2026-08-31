# PyVault

A Tkinter GUI password manager with an encrypted vault. Started as Day 29–30 of
*100 Days of Code*, then extended with real encryption, a master password
(Argon2id), breach checking, vault backup, and an account browser.

> **⚠️ Educational project — please read before trusting it with real passwords.**
> I built PyVault to learn cryptography, GUI development, and software release
> practices. It uses real encryption (Fernet via the `cryptography` library)
> and a real key-derivation function (Argon2id), but it has **not been
> security-audited**, and it has known gaps a mature password manager doesn't:
>
> - **Vault writes are not atomic.** A crash or power loss while saving can
>   truncate the vault file. Keep a backup.
> - **No idle auto-lock.** Once you unlock it, the vault stays unlocked until
>   you close the app.
> - **The Argon2 cost parameters are currently below OWASP guidance** and will
>   be raised before v2.0.0 final.
> - Passwords are shown in plaintext popups.
> - Clipboard auto-clear can't scrub Windows clipboard *history* (Win+V), and
>   won't fire if the app is closed mid-countdown.
>
> For accounts you actually care about, use an established password manager.
> Provided as-is, without warranty — see [LICENSE](LICENSE).

## Features

- **Master password (Argon2id)** — the vault is locked behind a password you
  choose. It is never stored: the encryption key is re-derived from it every
  time you unlock, and exists only in memory for that session. An old
  (pre-v2) vault is detected on startup and offered a one-way upgrade
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
- **Key backup and restore (v1 only)** — *Options → Export Vault Key* and
  *Import Vault Key* act on the old keyring key, which a v2 vault no longer
  uses. They remain only for recovering pre-v2 vaults and will be removed
- **Vault backup and restore** — *Options → Export Vault* saves a copy of your
  encrypted vault; *Import Vault* replaces it from a backup. Importing copies
  the current vault to `data.enc.bak` first, so a mistaken import is
  recoverable
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

Once it's open, see **[USAGE.md](USAGE.md)** for a walkthrough of everyday
tasks — generating and saving passwords, searching, the All Accounts window,
and backing up your vault.

## Where are my passwords stored?

In an **encrypted vault file** at `~/PyVault_Vault/data.enc` — your home
folder, deliberately *not* the program folder, so updating or re-downloading
PyVault never disturbs it. It's encrypted with
[Fernet](https://cryptography.io/en/latest/fernet/) (AES-128-CBC + HMAC).

**The encryption key is not stored anywhere.** It is derived from your master
password with [Argon2id](https://en.wikipedia.org/wiki/Argon2), a deliberately
slow, memory-hard function, every time you unlock the vault. It lives in memory
for that session and is gone when you close the app.

The vault file itself is a JSON envelope: a readable header holding the Argon2
parameters and a random per-vault salt, wrapped around the encrypted accounts.
Nothing in that header is secret — it is the recipe for rebuilding the key, and
it is useless without the password. Storing the parameters in the file is what
lets the cost settings be raised in a later release without locking you out of
an existing vault.

That is the whole design: **the vault file is useless without your master
password, and there is no copy of that password anywhere.**

## Backing up

Two things keep your passwords recoverable, and only one of them is a file.

**Your master password** — remember it. There is no copy of it anywhere, no
reset, no recovery email, and no back door. If you forget it, the vault is
lost, and that is the point of the design.

**Your vault** — *Options → Export Vault* writes a copy wherever you choose (or
copy `~/PyVault_Vault/data.enc` yourself). Do this regularly: vault writes are
not yet atomic, so a crash during a save can damage the file.

A vault backup is just ciphertext locked behind your master password, so it is
safe to keep in cloud storage — but choose a strong master password, because
anyone holding the file can attack it offline for as long as they like. Argon2
is what makes that expensive, not impossible.

### Restoring on a new machine

1. Install PyVault and run it once. It will offer to create a new vault —
   you can let it, or close it.
2. *Options → Import Vault*, and pick your vault backup (or copy `data.enc`
   back to `~/PyVault_Vault/` yourself).
3. Restart PyVault and unlock with your master password.

If a vault will not open, the cause is almost always a mistyped master
password. **Your passwords are still there** — the file is locked, not
damaged.

## Roadmap

Planned before **v2.0.0 final**:

- **Atomic vault writes** — saving currently truncates the vault file and then
  rewrites it, so a crash or power loss in between can leave it damaged. The
  fix is to write a temporary file alongside the vault, flush it to disk, and
  atomically replace the original, so a save either fully happens or does not
  happen at all
- **Argon2 cost parameters raised** to meet OWASP guidance. Existing vaults
  keep working — their parameters live in their own header
- **Readable error dialogs** in place of the tracebacks that a failed unlock
  or migration currently produces
- **Idle auto-lock** — clear the session after a period of inactivity, so an
  unlocked vault does not stay open on an unattended machine
- **Removal of the vestigial v1 key menu items**, which act on a keyring key
  that a v2 vault no longer uses
- **Test coverage** for unlock, save/load, and migration

Planned after that:

- **A refreshed interface** — the current window is plain Tkinter defaults.
  Restyling it with `ttk` widgets and a considered layout, so it looks like
  something you would choose to use rather than a class project

## Version history

See [CHANGELOG.md](CHANGELOG.md). Current release: **v2.0.0-beta.1** —
a beta. The last stable release is **v1.9.0**.

## License

[MIT](LICENSE)
