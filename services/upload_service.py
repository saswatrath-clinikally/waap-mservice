import httpx
from fastapi import HTTPException, status, Request

from config import settings
from constants import DEFAULT_TIMEOUT, HEADER_X_API_KEY

http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)


async def forward_upload_request(request: Request) -> tuple[bytes, int, str]:
    """
    Forwards raw multipart/form-data HTTP payload to clintel's /upload/v2 endpoint.
    """
    # Extract headers and filter out problematic ones for the proxy
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower()
        not in {"host", "content-length", "connection", "transfer-encoding"}
    }

    # Inject our internal auth key for clintel
    headers[HEADER_X_API_KEY] = settings.CLINTEL_BACKEND_X_API_KEY

    target_url = f"{settings.CLINTEL_BACKEND_URL.rstrip('/')}/upload/v2"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    try:
        # Read the raw stream of bytes (multipart/form-data exactly as sent by Express)
        body = await request.body()

        response = await http_client.post(
            target_url,
            content=body,
            headers=headers,
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with the upload backend: {str(exc)}",
        )

    return (
        response.content,
        response.status_code,
        response.headers.get("content-type", "application/octet-stream"),
    )
