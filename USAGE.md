# Using PyVault

A hands-on walkthrough of PyVault once it's open. For installing and starting
the app, see [README → How to run it](README.md#how-to-run-it); for where your
data lives and the design behind it, see
[README → Where are my passwords stored?](README.md#where-are-my-passwords-stored).

> **Before you store anything real, read the warning at the top of the
> [README](README.md).** PyVault is an educational project with no master
> password — anyone who can use your unlocked computer can open it and read
> every saved password. For accounts you actually care about, use an
> established password manager.

## A quick tour of the main window

```
  Website:          [ netflix.com        ]  [ Search ]
  Email/Username:   [ you@gmail.com                  ]
  Password:         [ ················· ] [ Generate Password ]

  [            Save            ]
  [        All Accounts        ]
```

- **Website / Email/Username / Password** — the three fields for one account.
  The email field starts pre-filled with `@gmail.com` so you only type the
  part in front; clear it if you use a different domain.
- **Generate Password** — fills the Password field with a fresh strong
  password and copies it to your clipboard.
- **Search** — looks up whatever website is typed in the Website field and
  shows its saved login.
- **Save** — writes the current three fields to your encrypted vault.
- **All Accounts** — opens a window listing every account you've saved.
- **Options** menu (top of the window) — key and vault backup/restore, and
  Exit.

## Everyday tasks

### Generate a strong password

1. Click **Generate Password**.
2. A 13-character password (letters, digits, and symbols) appears in the
   Password field and is **copied to your clipboard** automatically, ready to
   paste into the website you're signing up for.
3. The clipboard is **wiped after 10 seconds** — so paste it reasonably
   promptly. If you copy something else in the meantime, PyVault leaves your
   new clipboard alone and only clears its own password.

> Heads-up: on Windows, clipboard **history** (Win+V) can still hold a copy
> the auto-clear can't reach, and the clear won't fire if you close PyVault
> during the 10-second countdown.

### Save an account

1. Type the **Website**, **Email/Username**, and **Password** (or generate
   one). Website and Password can't be blank — PyVault will say *"Please enter
   all fields"* if either is empty.
2. Click **Save**.
3. Before saving, PyVault checks the password against the Have I Been Pwned
   breach database. If it's been seen in a known breach, you'll get a
   **"Password Found!"** prompt asking whether to use it anyway:
   - **No** — nothing is saved; pick a different password.
   - **Yes** — it saves as-is.
   - (If you're offline or the service is down, this check is skipped and
     saving continues normally.)
4. If you already have an entry for that website, you'll get an **"Overwrite
   Warning"**. Choose **Yes** to replace the old login or **No** to keep it —
   nothing is overwritten silently.
5. On success you'll see *"Successfully saved new account data!"*.

> The **very first** password you ever save creates the vault and its
> encryption key. PyVault reminds you not to delete the PyVault entry in your
> OS's key manager — if that key is gone, the vault can't be opened.

### Look up a saved password

1. Type the website into the **Website** field.
2. Click **Search**.
3. A popup shows the **email and password** saved for that site. If nothing's
   saved under that name, you'll get *"Account info not found!"* — check the
   spelling matches how you saved it.

### See everything at once (All Accounts)

1. Click **All Accounts**. A window opens listing every account as
   `website - email` (passwords stay hidden here).
2. **Double-click any row** to reveal that account's email and password —
   no need to close the window and retype the site into Search.
3. The window is a single instance: clicking **All Accounts** again just
   brings it to the front instead of opening a second copy. If you save a new
   account while it's open, the list rebuilds itself so it's never stale
   (it returns to its default position and scroll when it does).

### Delete an account

1. Open **All Accounts**.
2. **Click once** to highlight the account you want to remove.
3. Click **Delete Selected Account** and confirm. The entry is removed from
   the encrypted vault and disappears from the list.

> Deletion is permanent — there's no undo and no trash. If you're not sure,
> export a vault backup first (below).

## Keeping a backup

Restoring PyVault takes **two** things, and they're backed up separately:
your **key** and your **vault**. Both live in the **Options** menu. Do the key
export **now**, before you ever need it — without the key, a vault file can't
be opened, and there is no reset or recovery email.

### Export your key

**Options → Export Vault Key**, then choose where to save the `.key` file.
This file can decrypt your vault, so it's as sensitive as the passwords
themselves — keep it somewhere trusted (e.g. a USB stick in a drawer).

### Export your vault

**Options → Export Vault**, then choose where to save the `.enc` file. This
copy is just ciphertext — useless without the key — so it's the safe half to
keep in cloud storage.

> **Store the two apart.** Anyone who has *both* files has all your passwords.
> Key in one place, vault in another.

### Restore on a new machine

1. Install and run PyVault once.
2. **Options → Import Vault Key** and pick your key backup.
3. **Options → Import Vault** and pick your vault backup.

Importing the **key first** means the vault opens as soon as it lands. If you
import the vault first, PyVault warns that your key won't open it yet — just
bring the key across next. On import, PyVault copies any existing vault to
`data.enc.bak` first, so a mistaken import is recoverable.

## Dialogs you might see

| Message | What it means | What to do |
| --- | --- | --- |
| *Please enter all fields* | Website or Password was left blank | Fill both, then Save |
| *Password Found!* | The password appears in a known breach | **No** to choose another, **Yes** to save it anyway |
| *Overwrite Warning* | You already have an entry for this website | **Yes** replaces it, **No** keeps the old one |
| *Vault Can't Be Unlocked / Keys do not match* | The key in your keyring doesn't match this vault | **No**, then import the correct key — don't reset |
| *Old Vault file already exists! Overwrite?* | Importing over an existing vault | **Yes** overwrites (old one is copied to `.bak` first) |
| *No Key — import your key next…* | You imported a vault but have no key yet | Import your key backup next |

## Good habits

- **Export your key today.** It's the one piece that can never be regenerated.
- **Keep your key and vault in different places** — together they undo the
  encryption entirely.
- **Lock your computer.** With no master password, an unlocked machine is an
  open vault.
- **Paste generated passwords promptly** (10-second clipboard clear), and be
  aware of Windows clipboard history.

## Troubleshooting

- **"Vault Can't Be Unlocked" / "Keys do not match"** — almost always a key
  that doesn't match the vault, **not** lost data. Your passwords are still
  there; the file is locked, not damaged. Import the correct key rather than
  choosing to reset. (Resetting erases everything and starts fresh.)
- **Search says "Account info not found!"** — the website name must match what
  you saved. Open **All Accounts** to see the exact names.
- **Generated password didn't clear from the clipboard** — the auto-clear only
  fires if the clipboard still holds that password and PyVault is still open
  during the 10-second window; it also can't scrub Windows clipboard history.
- **App won't start** — see [README → How to run it](README.md#how-to-run-it).
  On Windows the launcher walks you through installing Python if it's missing.

---

For version history, see [CHANGELOG.md](CHANGELOG.md). Current release:
**v1.9.0**.
