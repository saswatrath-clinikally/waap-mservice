from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str


@router.get(
    "",
    response_model=HealthCheckResponse,
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    """
    return HealthCheckResponse(status="ok")
