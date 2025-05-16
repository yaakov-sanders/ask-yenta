from fastapi import APIRouter

from app.features.login.api_routes import router as login_router
from app.features.users.api_routes import router as users_router
from app.features.utils.api_routes import router as utils_router
from app.features.user_profile.api_routes import router as user_profile_router
from app.features.conversation_memory.api_routes import router as conversation_memory_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(utils_router)
api_router.include_router(user_profile_router)
api_router.include_router(conversation_memory_router)
