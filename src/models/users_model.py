from sqlmodel import Field

from src.models.base_model import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"

    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: str | None = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
