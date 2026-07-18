# Changelog

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
