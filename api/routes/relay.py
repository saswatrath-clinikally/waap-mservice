from fastapi import APIRouter, HTTPException, Request, Response

from constants import HTTP_400_BAD_REQUEST
from services.relay_service import forward_chat_request

router = APIRouter()


@router.post("/chat")
async def chat_relay(request: Request):
    """
    Acts as a pass-through proxy for the chat endpoint.
    Receives JSON from remote service -> Forwards to backend -> Returns response.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Invalid JSON payload"
        )

    content, status_code, media_type = await forward_chat_request(payload)

    return Response(
        content=content,
        status_code=status_code,
        media_type=media_type,
    )
