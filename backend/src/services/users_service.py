from typing import cast

from src.core.exceptions import DuplicatedError, UnauthorizedError
from src.core.security import create_access_token, hash_password, verify_password
from src.core.validators import validate_password
from src.models.users_model import User
from src.repository.users_repository import UsersRepository
from src.schemas.users_schemas import (
    UserCreate,
    UserCreateInternal,
    UserLogin,
    UserUpdate,
    UserUpdateInternal,
)
from src.services.base_service import BaseService


class UsersService(BaseService):
    def __init__(self, repository: UsersRepository) -> None:
        super().__init__(repository)
        self._repository: UsersRepository = repository

    async def register(self, payload: UserCreate) -> User:
        validate_password(payload.password)
        if await self._repository.get_by_email(payload.email):
            raise DuplicatedError(detail="A user with this email already exists")

        internal = UserCreateInternal(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        return cast(User, await self.add(internal))

    async def authenticate(self, credentials: UserLogin) -> str:
        user = await self._repository.get_by_email(credentials.email)
        if user is None or not verify_password(
            credentials.password, user.hashed_password
        ):
            raise UnauthorizedError(detail="Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError(detail="User account is inactive")
        return create_access_token(subject=str(user.id))

    async def modify(self, user_id: int, payload: UserUpdate) -> User:
        data = payload.model_dump(exclude_none=True)
        if "password" in data:
            validate_password(data["password"])
            data["hashed_password"] = hash_password(data.pop("password"))
        internal = UserUpdateInternal(**data)
        return cast(User, await self.patch(user_id, internal))
