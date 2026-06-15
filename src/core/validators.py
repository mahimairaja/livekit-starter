from fastapi import HTTPException


class PasswordValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


def validate_password(password: str) -> bool:
    if len(password) < 8:
        raise PasswordValidationError("Password must be at least 8 characters long")
    if not any(char.isupper() for char in password):
        raise PasswordValidationError(
            "Password must contain at least one uppercase letter"
        )
    if not any(char.islower() for char in password):
        raise PasswordValidationError(
            "Password must contain at least one lowercase letter"
        )
    return True
