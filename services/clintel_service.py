import json
import httpx
from fastapi import HTTPException, status
from agents.transformer import transformer
from config import settings
from constants import (
    DEFAULT_TIMEOUT,
    HEADER_CONTENT_TYPE,
    HEADER_X_API_KEY,
    CONTENT_TYPE_JSON,
)

# Global client to allow connection pooling and keep-alive across multiple proxy requests
http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)


async def _transform_backend_response(response: httpx.Response) -> bytes:
    content_type = response.headers.get(HEADER_CONTENT_TYPE.lower(), "")
    if CONTENT_TYPE_JSON not in content_type.lower():
        try:
            transformed_text = await transformer.transform(response.text)
            return transformed_text.encode("utf-8")
        except Exception:
            return response.content

    try:
        payload = response.json()
    except ValueError:
        return response.content

    try:
        transformed_payload = await transformer.transform_payload(payload)
    except Exception:
        return response.content

    return json.dumps(transformed_payload, ensure_ascii=False).encode("utf-8")


async def forward_chat_request(payload: dict) -> tuple[bytes, int, str]:
    headers = {
        HEADER_X_API_KEY: settings.CLINTEL_BACKEND_X_API_KEY,
        HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
    }

    try:
        response = await http_client.post(
            f"{settings.CLINTEL_BACKEND_URL.rstrip('/')}/chat",
            json=payload,
            headers=headers,
        )
        transformed_content = await _transform_backend_response(response)

        return (
            transformed_content,
            response.status_code,
            response.headers.get(HEADER_CONTENT_TYPE.lower(), CONTENT_TYPE_JSON),
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with the target backend: {str(e)}",
        )
