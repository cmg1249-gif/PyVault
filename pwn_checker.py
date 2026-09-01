import requests
import hashlib
PWNED_PW_ENDPOINT = "https://api.pwnedpasswords.com/range/"

def build_pwned_db(beg_hash: str) -> dict[str, int]:
	"""Takes the first 5 chars of hash and builds the data dictionary to compare against"""
	data = {
	}
	response = requests.get(url=f"{PWNED_PW_ENDPOINT}{beg_hash}", timeout=4)
	response.raise_for_status()
	for line in response.text.strip().splitlines():
		if ":" in line:
			key, value = line.split(":")
			data[key] = int(value)
	return data

def get_hash(pw: str) -> list[str]:
	"""Expects raw string, returns split hexa digits of pw"""
	sha1_hash: str = hashlib.sha1(pw.encode('utf-8')).hexdigest().upper()
	first_five_hash: str = sha1_hash[:5]
	rest_of_hash: str = sha1_hash[5:]
	return [first_five_hash, rest_of_hash]


def search_for_match_count(passwd: str) -> int:
	"""Uses get_hash and build_pwned_db to get a hash, build the database, then begins to search for matches"""
	# The divided hash is 5chars:35chars
	divided_hash: list = get_hash(passwd)
	pwned_db: dict = build_pwned_db(divided_hash[0])
	return pwned_db.get(divided_hash[1], 0)
