import pytest
from fastapi import HTTPException

from src.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("Password1")
    assert hashed != "Password1"
    assert ":" in hashed  # salt_hex:digest_hex
    assert verify_password("Password1", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_hash_password_uses_random_salt():
    assert hash_password("Password1") != hash_password("Password1")


def test_verify_password_rejects_malformed_hash():
    assert verify_password("Password1", "not-a-valid-hash") is False


def test_access_token_roundtrip():
    token = create_access_token(subject="42")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_decode_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc:
        decode_access_token("clearly.not.a.jwt")
    assert exc.value.status_code == 401
