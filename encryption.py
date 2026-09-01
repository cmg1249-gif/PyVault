from cryptography.fernet import InvalidToken

class MigrationError(Exception):
	"""Raised when a v2 migration fails"""
	pass
class VaultNotFoundError(Exception):
	"""Raised when a vault doesn't exist."""
	pass


class KeyNotFoundError(Exception):
	"""Raised when an operation needs the vault key but the keyring has none."""
	pass

class IncorrectPasswordError(Exception):
	"""User input is wrong password"""
	pass


import keyring
import keyring.errors
import json
from cryptography.fernet import Fernet
import os
from pathlib import Path
import shutil
import base64
from argon2.low_level import hash_secret_raw, Type


OLD_DATA_FILE = Path(__file__).parent / "data.enc"
HOME = Path.home()
VAULT_DIR = HOME.joinpath("./PyVault_Vault")
DATA_FILE = VAULT_DIR.joinpath("./data.enc")
DATA_FILE_BAK = VAULT_DIR.joinpath("./data.enc.bak")

HEADER_VERSION = 1
DEFAULT_PARAMS = dict(memory_cost=8 * 1024, time_cost=3, parallelism=4)
_session = None
_counter = 0

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
	"""v2 Encrypts the given dict and writes it to the vault file, replacing it."""
	if _session is None:
		raise KeyNotFoundError("Vault is Locked")

	url_safe_key_bytes = base64.urlsafe_b64encode(_session["key"])
	text: bytes = json.dumps(data).encode("utf-8")
	f = Fernet(url_safe_key_bytes)
	token: bytes = f.encrypt(text)
	vault_json = build_vault_text(_session["salt"],_session["memory_cost"],_session["time_cost"],_session["parallelism"], token)
	DATA_FILE.write_text(vault_json, "utf-8")

def load_data() -> dict:
	"""v2 Reads and decrypts the vault file, returning its contents as a dict."""
	if _session is None:
		raise KeyNotFoundError("Vault is Locked")

	header_params = parse_vault_text(DATA_FILE.read_text(encoding="utf-8"))
	url_safe_key_bytes = base64.urlsafe_b64encode(_session["key"])
	f = Fernet(url_safe_key_bytes)
	plain_text = f.decrypt(header_params["ciphertext"])
	pt_string: str = plain_text.decode("utf-8")
	pt_dict: dict = json.loads(pt_string)
	return pt_dict

def ensure_vault_dir() -> None:
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

def import_vault(source: str | Path) -> str | None:
	"""Replaces the vault with source, backing up any existing vault first.

	The current vault is copied to a fresh numbered backup name from
	next_backup_path() before being overwritten, so an import never
	destroys an earlier backup and a bad import is always recoverable:
	import that backup file to put it back. Returns the path the backup
	was written to, or None if there was no vault to back up.
	Deliberately does NOT check whether the password opens source - that
	is the wrapper's job (see import_vault_wrapper, which trial-opens the
	file first). Callers confirm overwrites with the user before calling.
	Raises VaultNotFoundError if source is not a file.
	"""
	path = Path(source)
	if not path.is_file():
		raise VaultNotFoundError("No vault found for user")
	Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
	backup = None
	if DATA_FILE.is_file():
		backup = next_backup_path()
		shutil.copy2(DATA_FILE, backup)
	shutil.copy2(source, DATA_FILE)
	return backup
def next_backup_path() -> str:
	n = 0
	candidate = DATA_FILE_BAK
	if not candidate.exists():
		return str(DATA_FILE_BAK)
	while candidate.exists():
		n += 1
		new_candidate_string =f"{str(DATA_FILE_BAK)}_{n}"
		new_candidate_path = Path(new_candidate_string)
		if new_candidate_path.exists():
			continue
		if not new_candidate_path.exists():
			return new_candidate_string
def delete_vault() -> None:
	"""Deletes the vault file and its key from the keyring.

	Tolerates either being absent already. Removing the key is what makes a
	reset genuinely fresh: the next save mints a new one.
	"""
	try:
		os.remove(DATA_FILE)
	except FileNotFoundError:
		pass

def to_b64(raw: bytes) -> str:
	"""Converts a bytes into a base64 encoded string."""
	base64_bytes = base64.b64encode(raw)
	base64_string = base64_bytes.decode()
	return base64_string



def from_b64(text: str) -> bytes:
	"""Converts a base64 encoded string into a bytes object."""
	base64_bytes = base64.b64decode(text)
	return base64_bytes

def build_vault_text(salt: bytes, memory_cost: int, time_cost: int, parallelism: int, ciphertext: bytes) -> str:
	"""Return the complete vault file content as a JSON string."""
	b64_salt = to_b64(salt)
	b64_ciphertext = to_b64(ciphertext)
	vault = {
		"version": HEADER_VERSION,
		"kdf": "argon2id",
		"salt": b64_salt,
		"memory_cost": memory_cost,
		"time_cost": time_cost,
		"parallelism": parallelism,
		"ciphertext": b64_ciphertext
	}
	return json.dumps(vault, indent=2)


def parse_vault_text(text: str) -> dict:
	"""Parse vault file content. Returns a dict with keys:
	     salt (bytes), memory_cost (int), time_cost (int),
	     parallelism (int), ciphertext (bytes)
	Raises ValueError on an unsupported version.
	"""
	json_str = json.loads(text)
	if json_str["version"] != HEADER_VERSION:
		raise ValueError("Unsupported version")
	else:
		ciphertext = from_b64(json_str["ciphertext"])
		salt = from_b64(json_str["salt"])
		json_str["ciphertext"] = ciphertext
		json_str["salt"] = salt
		return json_str
def create_key_using_pass(password: str, salt: bytes, memory_cost: int,
						  time_cost: int, parallelism: int) -> bytes:
	"""Create a 32-byte encryption key from a master password."""
	password_bytes = password.encode()
	secret = hash_secret_raw(secret=password_bytes, salt=salt, memory_cost=memory_cost,
							 time_cost=time_cost, parallelism=parallelism, hash_len=32, type=Type.ID)
	return secret

def create_vault(password: str, plaintext: str) -> str:
	"""Encrypt plaintext under a key derived from password.
	Returns the complete vault file content (JSON string)."""
	salt = os.urandom(16)
	key = create_key_using_pass(password,
								salt,DEFAULT_PARAMS["memory_cost"],
								DEFAULT_PARAMS["time_cost"],
								DEFAULT_PARAMS["parallelism"])

	url_safe_key_bytes = base64.urlsafe_b64encode(key)
	fernet = Fernet(url_safe_key_bytes)
	token = fernet.encrypt(plaintext.encode())

	vault = build_vault_text(salt=salt, memory_cost=DEFAULT_PARAMS["memory_cost"],
							 time_cost=DEFAULT_PARAMS["time_cost"],
							 parallelism=DEFAULT_PARAMS["parallelism"],ciphertext=token)

	return vault

def open_vault(password: str, file_text: str) -> str:
	"""Parse a vault file, re-derive the key, decrypt, return the plaintext.
	A wrong password will make Fernet raise InvalidToken — let it raise."""
	dict_ = parse_vault_text(file_text)
	key = create_key_using_pass(password, dict_['salt'], dict_['memory_cost'], dict_['time_cost'], dict_['parallelism'])
	url_safe_key_bytes = base64.urlsafe_b64encode(key)
	fernet = Fernet(url_safe_key_bytes)
	plaint_text = fernet.decrypt(dict_['ciphertext'])

	return plaint_text.decode()

def lock():
	global _session
	_session = None

def unlock(password):
	global _session
	header_params = parse_vault_text(DATA_FILE.read_text())
	key = create_key_using_pass(password,header_params["salt"],header_params["memory_cost"],
						  header_params["time_cost"],header_params["parallelism"])

	try:
		url_safe_key_bytes = base64.urlsafe_b64encode(key)
		f = Fernet(url_safe_key_bytes)
		f.decrypt(header_params["ciphertext"])
	except InvalidToken:
		raise IncorrectPasswordError("The password does not decrypt this vault")
	_session = {
		"key": key,
		"salt": header_params["salt"],
		"memory_cost": header_params["memory_cost"],
		"time_cost": header_params["time_cost"],
		"parallelism": header_params["parallelism"]
	}
def is_v1_vault() -> bool:
	if not DATA_FILE.is_file():
		return False
	try:
		json_text = json.loads(DATA_FILE.read_text(encoding="utf-8"))
		if json_text.get("version") is None:
			return True
		else:
			return False
	except json.JSONDecodeError:
		return True

def migrate_v1_to_v2(new_password: str) -> None:
	if not is_v1_vault():
		return
	#Backing up old vault and key before Migration
	export_vault(DATA_FILE_BAK)
	old_key = read_key()
	f = Fernet(old_key)
	accounts_json_b = f.decrypt(DATA_FILE.read_text(encoding="utf-8"))
	accounts_json_t = accounts_json_b.decode("utf-8")
	v2_vault = create_vault(new_password, accounts_json_t)
	DATA_FILE.write_text(v2_vault, encoding="utf-8")

	if open_vault(new_password, DATA_FILE.read_text(encoding="utf-8")) != accounts_json_t:
		#restore backup
		shutil.copy2(DATA_FILE_BAK, DATA_FILE)
		raise MigrationError("Migration Failed")
	try:
		keyring.delete_password(KEYRING_SERVICE,KEYRING_USER)
	except keyring.errors.PasswordDeleteError:
		pass


ensure_vault_dir()
