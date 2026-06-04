import logging
from fastapi import APIRouter, HTTPException

from services.bigquery_service import fetch_conversation_phone_numbers

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/conversation-numbers", response_model=list[str])
async def get_conversation_numbers():
    """
    Endpoint to retrieve the list of phone numbers from the BigQuery conversations table.
    """
    try:
        numbers = await fetch_conversation_phone_numbers()
        return numbers
    except Exception as e:
        logger.error(f"Failed to retrieve conversation numbers: {e}")
        raise HTTPException(status_code=500, detail="Error fetching numbers from BigQuery")
