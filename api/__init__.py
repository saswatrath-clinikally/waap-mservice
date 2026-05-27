from fastapi import APIRouter

from api.routes import health, chat, upload

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(upload.router, tags=["upload"])
