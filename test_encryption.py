"""Tests for the v2 (Argon2 + master password) crypto in encryption.py.

Run from the PyVault folder:      python -m pytest -v
Run just this file:               python -m pytest test_encryption.py -v

None of these tests touch your real vault. create_vault and open_vault
are string-in / string-out, so everything here happens in memory.
"""
import json

import pytest
from cryptography.fernet import InvalidToken

from encryption import (
	create_vault,
	open_vault,
	create_key_using_pass,
	parse_vault_text,
	DEFAULT_PARAMS,
)

# Values I invented. Nothing special about them — they just have to be
# the same on both sides of a test.
MASTER_PW = "correct-horse-battery-staple"
SECRET = "site: github | user: connor | pw: hunter2"


def test_round_trip():
	"""What goes in comes back out. The one test that matters most."""
	vault_text = create_vault(MASTER_PW, SECRET)
	assert open_vault(MASTER_PW, vault_text) == SECRET


def test_wrong_password_raises():
	"""A bad password must fail loudly, not return garbage."""
	vault_text = create_vault(MASTER_PW, SECRET)
	# pytest.raises means: this block MUST raise InvalidToken.
	# The test passes when it does, and fails when it doesn't.
	with pytest.raises(InvalidToken):
		open_vault("not-the-password", vault_text)


def test_plaintext_not_in_file():
	"""The secret must not be sitting in the file in readable form."""
	vault_text = create_vault(MASTER_PW, SECRET)
	assert SECRET not in vault_text


def test_key_is_deterministic():
	"""Same password + salt + params must always give the same key.

	This is the property that makes decryption possible at all, and the
	one that broke when PasswordHasher's auto-salt snuck in.
	"""
	salt = b"0123456789abcdef"  # fixed on purpose — no randomness here
	key1 = create_key_using_pass(MASTER_PW, salt, **DEFAULT_PARAMS)
	key2 = create_key_using_pass(MASTER_PW, salt, **DEFAULT_PARAMS)
	assert key1 == key2
	assert len(key1) == 32


# ---------------------------------------------------------------------
#  YOUR TURN — three more, same shapes as above
# ---------------------------------------------------------------------

def test_fresh_salt_each_create():
	"""Two vaults from identical inputs must NOT reuse the same salt.

	Comparing the whole file strings is too weak: Fernet picks a fresh IV
	on every encrypt, so two vaults come out different even when the salt
	is hardcoded. Parse the salt back out of each file and compare those.
	"""
	vault1 = create_vault(MASTER_PW, SECRET)
	vault2 = create_vault(MASTER_PW, SECRET)
	assert parse_vault_text(vault1)["salt"] != parse_vault_text(vault2)["salt"]


def test_salt_changes_key():
	"""Same password, different salt -> different key.

	Hint: shaped like test_key_is_deterministic, but with two different
	salt values and `!=` instead of `==`.
	"""
	salt1 = b"0123456789abcdee"  # fixed on purpose — no randomness here
	salt2 = b"0123456789abcdef"  # fixed on purpose — no randomness here
	key1 = create_key_using_pass(MASTER_PW, salt1, **DEFAULT_PARAMS)
	key2 = create_key_using_pass(MASTER_PW, salt2, **DEFAULT_PARAMS)
	assert key1 != key2
	assert len(key1) == 32


def test_bad_version_raises():
	"""A file claiming an unsupported version must be rejected.

	The header is plain JSON outside the ciphertext, so anyone can edit it.
	A future format could lay out the salt or params differently, and
	parsing one with today's rules would produce silent nonsense.
	"""
	header = json.loads(create_vault(MASTER_PW, SECRET))
	header["version"] = 99  # a version this build knows nothing about
	tampered_text = json.dumps(header)
	with pytest.raises(ValueError):
		parse_vault_text(tampered_text)
