from fastapi import APIRouter

from app.features.connections.connections_api import router as connections_router
from app.features.login.login_api import router as login_router
from app.features.users.users_api import router as users_router
from app.features.users_chat.user_chat_api import users_chat_router
from app.features.utils.api_routes import router as utils_router
from app.features.yenta_chat.yenta_chat_api import yenta_chat_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(utils_router)
api_router.include_router(yenta_chat_router)
api_router.include_router(connections_router)
api_router.include_router(users_chat_router)
