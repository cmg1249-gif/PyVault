# Changelog

## v1.9.0 — 2026-08-12

- **Double-click to reveal a password**: double-clicking a row in the *All
  Accounts* window now shows that account's email and password, instead of
  making you close the window and retype the site name into Search
- **Overwrite warning on save**: saving a website that already has an entry
  now asks before replacing it. Previously the new details silently
  overwrote the old ones, with no way to tell it had happened — and no way
  to get the old password back
- **All Accounts refreshes after a save**: with the window left open, saving
  a password used to leave the list showing the old contents until you closed
  and reopened it. It now rebuilds itself, so what's on screen matches the
  vault
- Note: the refresh rebuilds the window, so it returns to its default screen
  position and loses any scroll position
- **Fix (Windows launcher)**: `run.bat` decided whether Python was installed
  with `where python`. Windows ships "app execution alias" stubs named
  `python.exe` on machines with no Python at all — they exist only to open the
  Microsoft Store — so the check passed on exactly the machines it was meant
  to catch. The setup instructions never appeared, and the user got
  "check your internet connection" instead. The same stubs can be left
  dangling by a Store update, pointing at a package version that is gone.
  The launcher now runs Python rather than looking for the file
- **Install instructions now point at the Microsoft Store** as the easy path
  for Windows, with python.org kept as the alternative

## v1.8.0 — 2026-08-11

- **Vault backup and restore**: new *Options* menu items *Export Vault* and
  *Import Vault*, alongside the existing key backup. Export copies your
  encrypted vault to a file you choose; Import replaces the vault with a
  backup you pick. The two backups (key and vault) stay separate on purpose —
  a vault file is ciphertext and safe to store almost anywhere; the key is the
  sensitive half
- **Import backs up the old vault first**: before overwriting, the current
  `data.enc` is copied to `data.enc.bak`, so a mistaken import is always
  recoverable
- **Key-check on vault import**: if your current key does not open the vault
  you are importing, PyVault warns and lets you back out. If there is no key at
  all it tells you to import your key next — a restore may legitimately bring
  the vault across before its key, so this is allowed rather than blocked
- **Fix**: the key export dialog used `defaultextension="*.key"`, which could
  append a literal `*` to a typed filename; now `.key`
- **App icon**: PyVault now has a proper Windows icon, built from the project
  logo at every size from 16 to 256 pixels. The small sizes drop the "PyVault"
  ribbon and zoom the snake-and-lock emblem, which stays readable in the
  taskbar where the ribbon text would not
- **Desktop shortcut**: the first Windows launch offers to create one, and
  `make_shortcut.ps1` can create or repair it at any time. It resolves paths
  relative to itself, so PyVault works from whatever folder it's unpacked into
- **No console window after setup** (Windows): the launcher now starts the app
  with `pythonw` and exits immediately, instead of leaving a black window open
  for as long as PyVault is running. Setup only reappears if `requirements.txt`
  changes or an expected package stops importing
- **Fix**: setup treated any `PyVault.lnk` on the Desktop as a working
  shortcut. Installing into a new folder left the previous shortcut pointing
  at a folder that no longer existed, and setup skipped it as "already done" —
  leaving a shortcut that did nothing and no way to fix it short of deleting
  the marker file by hand. The existing shortcut's target is now checked, and
  repointed when it doesn't match
- Mac and Linux (`run.sh`) are unchanged: the terminal still stays open while
  the app runs, and there is no shortcut

## v1.7.0 — 2026-08-11

- **Key backup and restore**: new File menu with *Export Vault Key* and
  *Import Vault Key*. Export writes the vault key to a file you choose;
  import restores it — reinstalling Windows or moving to a new machine no
  longer means losing your vault
- **Import is validated before it commits**: the file is checked to be a
  well-formed key first, so a failed import leaves your keyring untouched
- **Mismatch warning**: importing a key that does not open your current
  vault warns that saved passwords would become unreadable and lets you
  back out. A key that matches (or a fresh install) imports silently
- Cancelling the export or import file dialog now does nothing instead of
  erroring

## v1.6.1 — 2026-08-09

- **Bug fix**: the logo is now loaded from a path anchored to the program
  file instead of the working directory, so launching PyVault from anywhere
  other than its own folder no longer fails to find it

## v1.6.0 — 2026-08-08

- **Vault moved out of the program folder** to `~/PyVault_Vault/data.enc`.
  Updating, re-downloading, or moving PyVault no longer looks like your
  passwords vanished — the vault lives in your home directory and survives
- **Automatic migration**: an existing `data.enc` sitting next to the program
  is moved to the new location on first launch. Runs once, never overwrites
  a vault that's already in the new spot
- **Fix**: "Delete vault and start fresh" now also removes the encryption key
  from the OS keyring. Previously the old key was reused, so a fresh vault
  was encrypted with the key from the vault you just discarded
- **Fix**: file paths no longer depend on the working directory the app was
  launched from — the vault and the legacy-file lookup both resolve to fixed
  locations regardless of how PyVault is started
- Deleting a vault that's already gone no longer raises

## v1.5.0 — 2026-08-08

- **Breach check on save (PwnCheck)**: before saving, passwords are checked
  against the Have I Been Pwned *Pwned Passwords* database — if the password
  has appeared in known breaches, a confirmation dialog lets you decide
  whether to save it anyway
- Privacy-preserving **k-anonymity** lookup: only the first 5 characters of
  the password's SHA-1 hash are ever sent; the password itself never leaves
  your machine
- Check is **best-effort**: if the service is unreachable (offline/timeout),
  saving proceeds normally — the vault never depends on the network
- `requests` added to requirements

## v1.4.3 — 2026-08-07

- Clicking All Accounts while the window is already open now raises it to
  the front (`lift()`) instead of doing nothing

## v1.4.2 — 2026-08-07

- **Bug fix**: closed the v1.4.1 known issue — All Accounts widgets are now
  built only when the window is created, so repeat clicks while it's open
  no longer stack duplicate widgets (quiet memory leak)

## v1.4.1 — 2026-08-07

- **Bug fix**: All Accounts window is now a singleton — clicking the button
  while the window is open no longer spawns duplicate windows, and closing
  it with the X properly resets state so it can be reopened
- Known issue: clicking All Accounts while the window is open re-creates
  its widgets in place (harmless, cleanup planned)

## v1.4.0 — 2026-08-07

- Password generator now uses the **`secrets` module** (cryptographically
  secure randomness) instead of `random`
- Character pools expanded via the `string` module: all ASCII letters,
  digits, and full punctuation set
- Cryptographically secure in-place shuffle (Fisher–Yates with
  `secrets.randbelow`)
- **Clipboard auto-clear**: generated passwords are wiped from the
  clipboard after 10 seconds (only if the clipboard still holds the
  password, so anything you copied in the meantime is left alone)

## v1.3.0 — 2026-07-18

- **Delete accounts** from the All Accounts window: click an entry, hit
  "Delete Selected Account", confirm — the account is removed from the
  encrypted vault and the list updates in place
- All Accounts window upgraded from a text box to a selectable list
  (one account per row, website + email)
- Confirmation dialog now stays attached to the All Accounts window instead
  of dropping it behind the main window
- Deleting a missing/already-deleted account is now a safe no-op

## v1.2.0 — 2026-07-17

- New **All Accounts** view: popup window listing every saved website and email (passwords stay hidden — search to reveal)
- Selectable/copyable text in the All Accounts window (Toplevel + Text widget)
- Rebranded to **PyVault** with new pixel-art logo (transparent background)
- Version number now shown in the title bar

## v1.1.0 — 2026-07-16

- Vault encryption with Fernet; key stored in the OS keyring
- Migration of existing plaintext JSON data into the encrypted vault
- Lost-key recovery flow (option to reset the vault)
- First-run warning about protecting the OS keyring entry

## v1.0.0 — 2026-07-15

- Initial release: password generator, save to file, search by website (Tkinter GUI)
