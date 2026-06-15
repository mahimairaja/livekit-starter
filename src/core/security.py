import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.core.config import config

oauth2_scheme = HTTPBearer()
agent_service_scheme = HTTPBearer()

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 and a random salt.

    Returns a ``salt_hex:digest_hex`` string that :func:`verify_password`
    can later validate.
    """
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split(":", maxsplit=1)
    except ValueError:
        return False

    salt = bytes.fromhex(salt_hex)
    expected_digest = bytes.fromhex(digest_hex)
    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(actual_digest, expected_digest)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY.get_secret_value(),
        algorithm=config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[config.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


async def get_current_user(
    token: Annotated[Any, Depends(oauth2_scheme)],
) -> int:
    payload = decode_access_token(token.credentials)
    sub = payload.get("sub")

    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return int(sub)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
