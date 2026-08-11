from cryptography.fernet import Fernet, InvalidToken


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

def import_key(destination: str | Path) -> None:
	"""
	Takes a destination path as input for Key location, then sets it as the new key
	:param destination:
	"""
	token: bytes = Path(destination).read_text(encoding="utf-8").strip().encode("utf-8")
	try:
		Fernet(token)
	except ValueError as err:
		raise KeyNotValidError("This file is not a key, or your key is corrupted") from err

	keyring.set_password(KEYRING_SERVICE, KEYRING_USER, token.decode("utf-8"))

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

def does_vault_exist():
	DATA_FILE.is_file()

def does_key_decrypt_vault(token):
	try:
		with open(DATA_FILE, "rb") as vault_file:
			vault: bytes = vault_file.read()
			f = Fernet(token)
			f.decrypt(vault)
			return True
	except InvalidToken:
		return False
migrate_data_to_home()


