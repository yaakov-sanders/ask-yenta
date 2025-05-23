from fastapi import APIRouter

from app.features.connections.api_routes import router as connections_router
from app.features.login.api_routes import router as login_router
from app.features.users.api_routes import router as users_router
from app.features.utils.api_routes import router as utils_router
from app.features.yenta_chat.api_routes import (
    router as yenta_chat_router,
)

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(utils_router)
api_router.include_router(yenta_chat_router)
api_router.include_router(connections_router, prefix="/connections", tags=["connections"])
