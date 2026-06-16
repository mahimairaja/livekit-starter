from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.core.container import Container
from src.schemas.token_schemas import RoomTokenRequest, RoomTokenResponse
from src.services.token_service import TokenService

router = APIRouter(prefix="/token", tags=["token"])


@router.post("", response_model=RoomTokenResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_room_token(
    payload: RoomTokenRequest,
    service: TokenService = Depends(Provide[Container.token_service]),
) -> RoomTokenResponse:
    # Public by default. To require an authenticated user, add the dependency
    # `current_user: CurrentUser` (see src/api/endpoints/users.py) to this
    # signature; LiveKit room tokens are unrelated to the backend's own JWT.
    return service.create_room_token(payload)
