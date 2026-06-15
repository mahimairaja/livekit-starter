import pytest
from pydantic import ValidationError

from src.core.config import (
    _PLACEHOLDER_JWT_SECRET,
    Config,
    _to_async_url,
    _url_requires_ssl,
)
from src.schemas.users_schemas import UserUpdate


def test_neon_url_coerced_to_asyncpg_and_libpq_params_stripped():
    url = "postgresql://u:p@ep-x.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    assert _to_async_url(url) == "postgresql+asyncpg://u:p@ep-x.aws.neon.tech/neondb"


def test_postgres_scheme_alias_coerced():
    assert _to_async_url("postgres://u:p@h:5432/db") == "postgresql+asyncpg://u:p@h:5432/db"


def test_existing_asyncpg_url_preserved():
    url = "postgresql+asyncpg://u:p@h:5432/db"
    assert _to_async_url(url) == url


def test_non_ssl_query_params_are_kept():
    out = _to_async_url("postgresql://u:p@h/db?application_name=app&sslmode=require")
    assert "application_name=app" in out
    assert "sslmode" not in out


def test_ssl_requirement_inference():
    assert _url_requires_ssl("postgresql://u:p@h/db?sslmode=require") is True
    assert _url_requires_ssl("postgresql://u:p@h/db?sslmode=verify-full") is True
    assert _url_requires_ssl("postgresql://u:p@h/db?sslmode=disable") is False
    assert _url_requires_ssl("postgresql://u:p@h/db?sslmode=prefer") is None
    assert _url_requires_ssl("postgresql://u:p@h/db") is None


def test_user_update_omits_privileged_fields():
    # Mass-assignment guard: clients must not be able to set role/status.
    fields = set(UserUpdate.model_fields)
    assert "is_superuser" not in fields
    assert "is_active" not in fields


def test_prod_rejects_placeholder_jwt_secret():
    with pytest.raises(ValidationError):
        Config(ENV="prod", JWT_SECRET_KEY=_PLACEHOLDER_JWT_SECRET)


def test_prod_rejects_short_jwt_secret():
    with pytest.raises(ValidationError):
        Config(ENV="prod", JWT_SECRET_KEY="too-short")


def test_prod_accepts_strong_jwt_secret():
    cfg = Config(ENV="prod", JWT_SECRET_KEY="x" * 40)
    assert cfg.ENV.value == "prod"


def test_dev_allows_placeholder_secret():
    cfg = Config(ENV="dev", JWT_SECRET_KEY=_PLACEHOLDER_JWT_SECRET)
    assert cfg.DEBUG is True
