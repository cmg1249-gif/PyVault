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
	"""Two vaults from identical inputs must NOT be identical files.

	Hint: call create_vault twice with the same password and secret,
	then assert the two strings differ. If they match, the salt isn't
	fresh per call.
	"""
	pass


def test_salt_changes_key():
	"""Same password, different salt -> different key.

	Hint: shaped like test_key_is_deterministic, but with two different
	salt values and `!=` instead of `==`.
	"""
	pass


def test_bad_version_raises():
	"""A file claiming an unsupported version must be rejected.

	Hint: create a vault, json.loads it into a dict, set its "version"
	to 99, json.dumps it back, then use pytest.raises(ValueError)
	around parse_vault_text on that text.
	"""
	pass
