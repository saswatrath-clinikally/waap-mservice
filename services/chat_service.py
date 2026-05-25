import json
import httpx
from fastapi import HTTPException
from agents import transformer
from config import settings
from constants import (
    DEFAULT_TIMEOUT,
    HEADER_CONTENT_TYPE,
    HEADER_X_API_KEY,
    CONTENT_TYPE_JSON,
    HTTP_502_BAD_GATEWAY,
)


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
        HEADER_X_API_KEY: settings.CLINTEL_BACKEND_API_KEY,
        HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.CLINTEL_BACKEND_URL.rstrip('/')}/chat",
                json=payload,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )
            transformed_content = await _transform_backend_response(response)

            return (
                transformed_content,
                response.status_code,
                response.headers.get(HEADER_CONTENT_TYPE.lower(), CONTENT_TYPE_JSON),
            )

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with the target backend: {str(e)}",
            )
