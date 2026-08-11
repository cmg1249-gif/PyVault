"""Tests for pwn_checker.

Run with:  python test_pwn_checker.py

These hit the real Have I Been Pwned API, so they need an internet
connection. The counts only ever go up, so the assertions check
"greater than" rather than exact numbers.
"""
import pwn_checker


def test_get_hash_splits_correctly():
	"""SHA-1 of 'password' is a known value, split 5 + 35."""
	prefix, suffix = pwn_checker.get_hash("password")
	assert prefix == "5BAA6", f"expected prefix 5BAA6, got {prefix}"
	assert suffix == "1E4C9B93F3F0682250B6CF8331B7EE68FD8", f"bad suffix: {suffix}"
	assert len(prefix) + len(suffix) == 40, "a SHA-1 hash is 40 hex chars"


def test_hash_is_uppercase():
	"""The API returns uppercase, so our hash must be uppercase to match."""
	prefix, suffix = pwn_checker.get_hash("password")
	assert prefix.isupper(), "prefix must be uppercase or lookups silently fail"
	assert suffix.isupper(), "suffix must be uppercase or lookups silently fail"


def test_build_pwned_db_returns_populated_dict():
	"""A known prefix should come back with hundreds of suffix:count pairs."""
	data = pwn_checker.build_pwned_db("5BAA6")
	assert isinstance(data, dict), "should return a dict"
	assert len(data) > 100, f"expected a full bucket, got {len(data)} entries"


def test_counts_are_integers():
	"""Values must be ints so callers can compare and format them."""
	data = pwn_checker.build_pwned_db("5BAA6")
	sample = next(iter(data.values()))
	assert isinstance(sample, int), f"counts should be int, got {type(sample).__name__}"


def test_known_breached_password():
	"""'password' is the most-breached password there is."""
	count = pwn_checker.search_for_match_count("password")
	assert count > 1_000_000, f"expected millions of hits, got {count}"


def test_clean_password_returns_zero():
	"""A random string should not appear in any breach."""
	count = pwn_checker.search_for_match_count("xK9$mQ2vLp7!zR-nT4wB")
	assert count == 0, f"expected 0 for a random password, got {count}"


def test_return_type_is_always_int():
	"""Both the found and not-found paths must return int, never str."""
	found = pwn_checker.search_for_match_count("password")
	clean = pwn_checker.search_for_match_count("xK9$mQ2vLp7!zR-nT4wB")
	assert isinstance(found, int), "breached path must return int"
	assert isinstance(clean, int), "clean path must return int"


if __name__ == "__main__":
	tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
	failures = 0
	for t in tests:
		try:
			t()
			print(f"PASS  {t.__name__}")
		except AssertionError as e:
			failures += 1
			print(f"FAIL  {t.__name__}: {e}")
	print()
	print(f"{len(tests) - failures} passed, {failures} failed")
