from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.users_model import User
from src.repository.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(
        self,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        super().__init__(session_factory=session_factory, model=User)

    async def get_by_email(self, email: str) -> User | None:
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalars().first()
