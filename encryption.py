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

def get_key():
	"""Gets key from keyring, returns key, makes one if there isn't one"""
	saved_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
	if saved_key is None:
		key = Fernet.generate_key()
		keyring.set_password(KEYRING_SERVICE, KEYRING_USER, key.decode("utf-8"))
		return key
	else:
		return saved_key.encode("utf-8")
def save_data(data):
	text = json.dumps(data).encode("utf-8")
	f = Fernet(get_key())
	token = f.encrypt(text)
	with open(DATA_FILE, "wb") as file:
		file.write(token)


def load_data():
	with open(DATA_FILE, "rb") as token_file:
		token = token_file.read()
		f = Fernet(get_key())
		token = f.decrypt(token)
		token_string = token.decode("utf-8")
		token_dict = json.loads(token_string)
		return token_dict


def convert_json():
	if not os.path.exists(OLD_DATA_FILE_JSON):
		return
	else:
		with open(OLD_DATA_FILE_JSON, "r") as file:
			data = json.load(file)
			save_data(data)
		os.remove(OLD_DATA_FILE_JSON)

def migrate_data_to_home():
	if DATA_FILE.is_file():
		return
	if not OLD_DATA_FILE.is_file():
		Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
	if OLD_DATA_FILE.is_file():
		# Make the vault DIR if it's not there
		Path.mkdir(VAULT_DIR, exist_ok=True, parents=True)
		shutil.move(OLD_DATA_FILE, DATA_FILE)







def delete_vault():
	try:
		os.remove(DATA_FILE)
	except FileNotFoundError:
		pass
	try:
		keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)
	except keyring.errors.PasswordDeleteError:
		pass

migrate_data_to_home()


