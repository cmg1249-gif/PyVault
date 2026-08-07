# Changelog

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
