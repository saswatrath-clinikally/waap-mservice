import json
import httpx
from fastapi import HTTPException, status
from agents.transformer import transformer
from clients.redis_client import get_thread_id, set_thread_id
from config import settings
from constants import (
    DEFAULT_TIMEOUT,
    HEADER_CONTENT_TYPE,
    HEADER_X_API_KEY,
    CONTENT_TYPE_JSON,
)

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


async def forward_chat_request(
    phone_number: str | None, payload: dict
) -> tuple[bytes, int, str]:
    existing_thread: str | None = None
    if phone_number:
        existing_thread = await get_thread_id(phone_number)
        if existing_thread:
            payload["thread_id"] = existing_thread

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
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with the target backend: {str(e)}",
        )

    if phone_number:
        try:
            resp_payload = response.json()
            new_thread_id: str | None = resp_payload.get("thread_id")
            if new_thread_id and new_thread_id != existing_thread:
                await set_thread_id(phone_number, new_thread_id)
        except ValueError:
            pass

    transformed_content = await _transform_backend_response(response)

    return (
        transformed_content,
        response.status_code,
        response.headers.get(HEADER_CONTENT_TYPE.lower(), CONTENT_TYPE_JSON),
    )