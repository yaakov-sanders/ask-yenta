from fastapi import APIRouter

from app.features.users.api_routes import router as users_router
from app.features.login.api_routes import router as login_router
from app.features.items.api_routes import router as items_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(items_router)
