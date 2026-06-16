from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.base_schema import ModelBaseInfo

# ---- Request payloads ------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    # Self-service fields only. Privileged fields (is_active, is_superuser) are
    # intentionally NOT here to prevent mass-assignment privilege escalation;
    # role/status changes belong in an admin-only flow.
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    full_name: str | None = None


# ---- Responses -------------------------------------------------------------


class UserRead(ModelBaseInfo):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Internal schemas ------------------------------------------------------
# The generic repository builds rows via ``Model(**schema.model_dump())`` and
# updates via ``schema.model_dump(exclude_none=True)``. These shape the data so
# only persistable columns (e.g. ``hashed_password``, never raw ``password``)
# ever reach the model.


class UserCreateInternal(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str | None = None


class UserUpdateInternal(BaseModel):
    email: EmailStr | None = None
    hashed_password: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
