from fastapi import APIRouter

from src.api.endpoints.users import router as users_router

routers = APIRouter(prefix="/v1")
routers.include_router(users_router)
