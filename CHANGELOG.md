# Changelog

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
