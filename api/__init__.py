from fastapi import APIRouter

from api.routes import health, chat

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
