import json
import logging
import httpx
from fastapi import HTTPException, status, Request

from config import settings
from constants import DEFAULT_TIMEOUT, HEADER_X_API_KEY

logger = logging.getLogger(__name__)
http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)


async def forward_upload_request(request: Request) -> tuple[bytes, int, str]:
    """
    Forwards raw multipart/form-data HTTP payload to clintel's /upload/v2 endpoint.
    """
    # Extract headers and filter out problematic ones for the proxy
    # Also filter out the incoming "x-api-key" so we don't send conflicting keys!
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower()
        not in {
            "host",
            "content-length",
            "connection",
            "transfer-encoding",
            "x-api-key",
        }
    }

    # Inject our internal auth key for clintel
    headers[HEADER_X_API_KEY] = settings.CLINTEL_BACKEND_X_API_KEY

    target_url = f"{settings.CLINTEL_BACKEND_URL.rstrip('/')}/upload/v2"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    try:
        # Read the raw stream of bytes (multipart/form-data exactly as sent by Express)
        body = await request.body()

        logger.info(f"\n--- SENDING UPLOAD REQUEST TO CLINTEL ---\nTarget URL: {target_url}\nHeaders (Sanitized): {json.dumps(headers, indent=2)}\nPayload: [Raw Multipart Binary Data - {len(body)} bytes]\n-----------------------------------------")

        response = await http_client.post(
            target_url,
            content=body,
            headers=headers,
        )

        try:
            formatted_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
            logger.info(f"\n--- RAW UPLOAD RESPONSE FROM CLINTEL ---\n{formatted_json}\n-----------------------------------------")
        except Exception:
            logger.info(f"\n--- RAW UPLOAD RESPONSE FROM CLINTEL ---\n{response.text}\n-----------------------------------------")

    except httpx.HTTPError as exc:
        logger.error(f"HTTPError communicating with upload backend: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with the upload backend: {str(exc)}",
        )

    return (
        response.content,
        response.status_code,
        response.headers.get("content-type", "application/octet-stream"),
    )
