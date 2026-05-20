from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    name: str
    version: str
    status: str

@router.get(
    "",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthCheck:
    """
    Health check endpoint.
    """
    return HealthCheck(
        name="wapp-middleware",
        version="0.1.0",
        status="OK"
    )
