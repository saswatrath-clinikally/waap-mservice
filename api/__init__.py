from fastapi import APIRouter

from api.routes import health, relay

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(relay.router, tags=["chat"])
