from typing import Annotated, cast

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.core.container import Container
from src.core.exceptions import PermissionDeniedError
from src.core.security import get_current_user
from src.models.users_model import User
from src.schemas.base_schema import FindBase
from src.schemas.users_schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)
from src.services.users_service import UsersService

router = APIRouter(prefix="/users")


@inject
async def get_current_user_record(
    user_id: Annotated[int, Depends(get_current_user)],
    service: UsersService = Depends(Provide[Container.users_service]),
) -> User:
    """Load the authenticated user's record (raises 404 if the account is gone)."""
    return cast(User, await service.get_by_id(user_id))


# The full authenticated user record; gives endpoints access to id + is_superuser.
CurrentUser = Annotated[User, Depends(get_current_user_record)]


def _require_self_or_admin(actor: User, target_user_id: int) -> None:
    if actor.id != target_user_id and not actor.is_superuser:
        raise PermissionDeniedError(detail="Not permitted to access this user")


def _require_admin(actor: User) -> None:
    if not actor.is_superuser:
        raise PermissionDeniedError(detail="Administrator privileges required")


# ---- Public: obtain or create credentials ----------------------------------


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
@inject
async def register_user(
    payload: UserCreate,
    service: UsersService = Depends(Provide[Container.users_service]),
):
    return await service.register(payload)


@router.post("/login", response_model=Token, tags=["auth"])
@inject
async def login(
    payload: UserLogin,
    service: UsersService = Depends(Provide[Container.users_service]),
) -> Token:
    return Token(access_token=await service.authenticate(payload))


# ---- Protected: require a valid Bearer token -------------------------------


@router.get("/me", response_model=UserRead, tags=["auth"])
async def read_me(current_user: CurrentUser):
    return current_user


@router.get(
    "",
    response_model=list[UserRead],
    tags=["users", "mcp-tools"],
    operation_id="list_users",
)
@inject
async def list_users(
    current_user: CurrentUser,
    service: UsersService = Depends(Provide[Container.users_service]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
):
    # Listing/enumerating all accounts is an admin-only operation.
    _require_admin(current_user)
    result = await service.get_list(
        FindBase(page=page, page_size=page_size, search=search),
        searchable_fields=["full_name", "email"],
    )
    return result["founds"]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    tags=["users", "mcp-tools"],
    operation_id="get_user",
)
@inject
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    service: UsersService = Depends(Provide[Container.users_service]),
):
    _require_self_or_admin(current_user, user_id)
    if user_id == current_user.id:
        return current_user
    return await service.get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserRead, tags=["users"])
@inject
async def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: CurrentUser,
    service: UsersService = Depends(Provide[Container.users_service]),
):
    _require_self_or_admin(current_user, user_id)
    return await service.modify(user_id, payload)


@router.delete("/{user_id}", tags=["users"])
@inject
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    service: UsersService = Depends(Provide[Container.users_service]),
):
    _require_self_or_admin(current_user, user_id)
    return await service.remove_by_id(user_id)
