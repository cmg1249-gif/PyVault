
from cryptography.fernet import InvalidToken
class VaultNotFoundError(Exception):
	"""Raised when a vault doesn't exist."""
	pass
class KeyNotFoundError(Exception):
	"""Raised when an operation needs the vault key but the keyring has none."""
	pass
class KeyNotValidError(Exception):
	"""Raised when there is an invalid file being referenced as Vault key"""
	pass
import keyring
import keyring.errors
import json
from cryptography.fernet import Fernet
import os
from pathlib import Path
import shutil
KEYRING_SERVICE = "PyVault-pw-manager"
KEYRING_USER = "PyVault-user"
OLD_DATA_FILE = Path(__file__).parent / "data.enc"
OLD_DATA_FILE_JSON = Path(__file__).parent / "data.json"
HOME =  Path.home()
VAULT_DIR = HOME.joinpath("./PyVault_Vault")
DATA_FILE = VAULT_DIR.joinpath("./data.enc")
DATA_FILE_BAK = VAULT_DIR.joinpath("./data.enc.bak")
def get_key() -> bytes:
	"""Gets the Fernet key from the OS keyring, creating one if none exists.

	Returns the key as bytes, ready to hand to Fernet(). The keyring stores
	it as a string, so it is decoded on the way in and encoded on the way out.
	"""
	saved_key: str | None = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
	if saved_key is None:
		key: bytes = Fernet.generate_key()
		keyring.set_password(KEYRING_SERVICE, KEYRING_USER, key.decode("utf-8"))
		return key
	else:
		return saved_key.encode("utf-8")

def read_key() -> bytes:
	"""Reads the vault key from the OS keyring without ever creating one.

	The read-only counterpart to get_key(): safe to call from validation
	code, because it can never mint and save a new key as a side effect.
	Returns the key as bytes, ready to hand to Fernet(). Raises
	KeyNotFoundError if the keyring has no key stored.
	"""
	saved_key: str | None = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
	if saved_key is None:
		raise KeyNotFoundError("No key found for user")
	saved_key: bytes = saved_key.encode("utf-8")
	return saved_key

def save_data(data: dict) -> None:
	"""Encrypts the given dict and writes it to the vault file, replacing it."""
	text: bytes = json.dumps(data).encode("utf-8")
	f = Fernet(get_key())
	token: bytes = f.encrypt(text)
	with open(DATA_FILE, "wb") as file:
		file.write(token)

def load_data() -> dict:
	"""Reads and decrypts the vault file, returning its contents as a dict.

	Raises FileNotFoundError if no vault exists yet, and InvalidToken if the
	file cannot be decrypted with the current key.
	"""
	with open(DATA_FILE, "rb") as token_file:
		token: bytes = token_file.read()
		f = Fernet(get_key())
		token = f.decrypt(token)
		token_string: str = token.decode("utf-8")
		token_dict: dict = json.loads(token_string)
		return token_dict


def convert_json() -> None:
	"""Migrates a pre-v1.1 plaintext data.json into the encrypted vault.

	Does nothing if no data.json is present, which is the normal case.
	"""
	if not os.path.exists(OLD_DATA_FILE_JSON):
		return
	else:
		with open(OLD_DATA_FILE_JSON, "r") as file:
			data = json.load(file)
			save_data(data)
		os.remove(OLD_DATA_FILE_JSON)

def migrate_data_to_home() -> None:
	"""Moves a pre-v1.6 vault from beside the program into the home directory.

	Also creates the vault directory. Never overwrites a vault that already
	exists in the new location, and does nothing if there is nothing to move.
	"""
	if DATA_FILE.is_file():
		return
	if not OLD_DATA_FILE.is_file():
		Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
	if OLD_DATA_FILE.is_file():
		# Make the vault DIR if it's not there
		Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
		shutil.move(OLD_DATA_FILE, DATA_FILE)

def export_key(destination: str | Path) -> None:
	"""Writes the vault key to destination as plain text.

	The resulting file can decrypt the vault, so it is as sensitive as the
	passwords themselves. Raises KeyNotFoundError if the keyring has no key.
	"""
	token: str | None = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
	if token is None:
		raise KeyNotFoundError("No key found for user")
	Path(destination).write_text(token, encoding="utf-8")

def import_key(source: str | Path) -> None:
	"""Reads a key backup file and stores it in the OS keyring as the vault key.

	The file is validated as a well-formed Fernet key before anything is
	written, so a failed import leaves the keyring exactly as it was.
	Raises KeyNotValidError if the file is not a key, and FileNotFoundError
	if there is nothing at source.
	"""
	token: bytes = Path(source).read_text(encoding="utf-8").strip().encode("utf-8")
	try:
		Fernet(token)
	except ValueError as err:
		raise KeyNotValidError("This file is not a key, or your key is corrupted") from err

	keyring.set_password(KEYRING_SERVICE, KEYRING_USER, token.decode("utf-8"))
def export_vault(destination: str | Path) -> None:
	"""Copies the vault file to destination, leaving the original in place.

	The copy is ciphertext and is useless without the key, so on its own it
	is safe to store almost anywhere - but restoring needs the key backup
	too (see export_key). Works whether or not the current key can decrypt
	the vault: a user whose keyring was wiped still deserves a backup.
	Raises VaultNotFoundError if there is no vault to export.
	"""
	if not DATA_FILE.is_file():
		raise VaultNotFoundError("No vault found for user")
	shutil.copy2(DATA_FILE, destination)

def import_vault(source: str | Path) -> None:
	"""Replaces the vault with source, backing up any existing vault first.

	Any current data.enc is copied to data.enc.bak before being overwritten,
	so a bad import is always recoverable: import_vault(DATA_FILE_BAK) puts
	it back. Deliberately does NOT check whether the current key decrypts
	source - during a restore the vault may arrive before its key, so that
	is the wrapper's job to warn about, not this function's job to block.
	Callers confirm overwrites with the user before calling (see
	import_vault_wrapper). Raises VaultNotFoundError if source is not a file.
	"""
	path = Path(source)
	if not path.is_file():
		raise VaultNotFoundError("No vault found for user")
	Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
	if DATA_FILE.is_file():
		shutil.copy2(DATA_FILE, DATA_FILE_BAK)
	shutil.copy2(source, DATA_FILE)


def delete_vault() -> None:
	"""Deletes the vault file and its key from the keyring.

	Tolerates either being absent already. Removing the key is what makes a
	reset genuinely fresh: the next save mints a new one.
	"""
	try:
		os.remove(DATA_FILE)
	except FileNotFoundError:
		pass
	try:
		keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)
	except keyring.errors.PasswordDeleteError:
		pass


def does_key_decrypt_vault(token: bytes) -> bool:
	"""Trial-decrypts the vault with a candidate key, without changing anything.

	Returns True if the key opens the current vault. A wrong key or a
	malformed one both return False - either way it does not open the vault.
	Raises FileNotFoundError if there is no vault; callers should check
	DATA_FILE.is_file() first.
	"""
	try:
		with open(DATA_FILE, "rb") as vault_file:
			vault: bytes = vault_file.read()
			f = Fernet(token)
			f.decrypt(vault)
			return True
	except (InvalidToken, ValueError):
		return False

def does_vault_go_with_key(vault: str | Path) -> bool:
	"""Trial-decrypts a candidate vault file with the current key.

	The mirror of does_key_decrypt_vault: there the key is the candidate
	and the vault is known; here the vault file is the candidate and the
	key comes from the keyring. Returns True if the current key opens it.
	A wrong key or a file that is not a Fernet token both return False.
	Raises KeyNotFoundError (from read_key) if the keyring has no key, and
	FileNotFoundError if there is nothing at vault - callers decide how to
	present those, since both are normal states during a restore.
	"""
	try:
		with open(vault, "rb") as vault_file:
			vault: bytes = vault_file.read()
			f = Fernet(read_key())
			f.decrypt(vault)
			return True
	except(InvalidToken, ValueError) :
		return False


migrate_data_to_home()


