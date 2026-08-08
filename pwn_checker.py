import requests
import hashlib
PWNED_PW_ENDPOINT = "https://api.pwnedpasswords.com/range/"
# first_5_sha_chars = "7288E"
# rest_sha_chars ="dd0fc3ffcbe93a0cf06e3568e28521687bc".upper()
# all_sha_chars = "7288edd0fc3ffcbe93a0cf06e3568e28521687bc".upper()

data = {
}
def check_pwned(beg_hash):
	response = requests.get(url=f"{PWNED_PW_ENDPOINT}{beg_hash}")
	for response in response.text.strip().splitlines():
		if ":" in response:
			key, value = response.split(":")
			data[key] = value


def get_hash(pw):
	sha1_hash = hashlib.sha1(pw.encode('utf-8')).hexdigest()
	first_five_hash = sha1_hash[:5]
	rest_of_hash = sha1_hash[5:]
	return [sha1_hash, first_five_hash, rest_of_hash]

hash_list = get_hash("password")

print(hash_list[1])