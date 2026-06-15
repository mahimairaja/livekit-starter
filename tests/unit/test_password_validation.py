import pytest

from src.core.validators import PasswordValidationError, validate_password


def test_valid_password_passes():
    assert validate_password("Password1") is True


@pytest.mark.parametrize(
    "password",
    [
        "short1A",  # too short (< 8)
        "lowercase1",  # no uppercase
        "UPPERCASE1",  # no lowercase
    ],
)
def test_invalid_passwords_raise(password):
    with pytest.raises(PasswordValidationError):
        validate_password(password)
