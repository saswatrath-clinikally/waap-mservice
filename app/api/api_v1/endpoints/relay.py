import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

class RelayResponse(BaseModel):
    status: str
    response_from_other: str | dict | None = None

@router.post("/send-hi", response_model=RelayResponse)
async def send_hi():
    """
    Sends a 'hi' message to the other backend running on port 8080.
    """
    headers = {
        "X-Api-Key": settings.OTHER_BACKEND_API_KEY,
        "Content-Type": "application/json"
    }
    # Sending a simple JSON payload. You can change this if the other backend expects a different format.
    payload = {"message": "hi"}
    
    async with httpx.AsyncClient() as client:
        try:
            # Assuming the other backend accepts a POST request at its root "/"
            response = await client.post(
                f"{settings.OTHER_BACKEND_URL}/", 
                json=payload, 
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            
            # Try to parse JSON response if possible, otherwise return text
            try:
                resp_data = response.json()
            except ValueError:
                resp_data = response.text
                
            return RelayResponse(status="success", response_from_other=resp_data)
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to communicate with other backend: {str(e)}"
            )
