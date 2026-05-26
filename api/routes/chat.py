from fastapi import APIRouter, Response

from services.clintel_service import forward_chat_request
from schemas.chat import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(
    chat_request: ChatRequest,
    response: Response,
):
    """
    Acts as a pass-through proxy for the chat endpoint.
    Receives JSON from remote service -> Forwards to backend -> Returns response.
    """
    # Extract all properties from Pydantic model (including 'extra' allowed fields)
    payload = chat_request.model_dump(exclude_none=True)
    phone_number = payload.get("phone_number")

    content, status_code, media_type = await forward_chat_request(
        phone_number, payload
    )

    return Response(
        content=content,
        status_code=status_code,
        media_type=media_type,
    )
