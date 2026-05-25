from fastapi import APIRouter, Depends, Response, status

from services.relay_service import forward_chat_request
from auth.security import get_api_key
from schemas.chat import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat_relay(
    chat_request: ChatRequest,
    response: Response,
    is_authenticated: bool = Depends(get_api_key),
):
    """
    Acts as a pass-through proxy for the chat endpoint.
    Receives JSON from remote service -> Forwards to backend -> Returns response.
    """
    if not is_authenticated:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "response": "Unauthorized api call",
            "thread_id": chat_request.thread_id or "",
        }

    # Extract all properties from Pydantic model (including 'extra' allowed fields)
    payload = chat_request.model_dump(exclude_none=True)

    content, status_code, media_type = await forward_chat_request(payload)

    return Response(
        content=content,
        status_code=status_code,
        media_type=media_type,
    )

    content, status_code, media_type = await forward_chat_request(payload)

    return Response(
        content=content,
        status_code=status_code,
        media_type=media_type,
    )
