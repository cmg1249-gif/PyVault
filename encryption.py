import keyring
import json
from cryptography.fernet import Fernet
import os
KEYRING_SERVICE = "connor-mylock-pw-manager"
KEYRING_USER = "connor-mylock-user"
DATA_FILE = "data.enc"

def get_key():
	"""Gets key from keyring, returns key, makes one if there isnt one"""
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


def migrate():
	if not os.path.exists("data.json"):
		return
	else:
		with open("data.json", "r") as file:
			data = json.load(file)
			save_data(data)
		os.remove("data.json")
def delete_vault():
	os.remove(DATA_FILE)


