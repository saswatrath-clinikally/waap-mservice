import json

import httpx
import pytest

from services import relay_service


@pytest.mark.asyncio
async def test_transform_backend_response_json_payload(monkeypatch):
    async def fake_transform_payload(payload):
        if isinstance(payload, dict) and "response" in payload:
            return {**payload, "response": "Clara says to use a gentle cleanser."}
        return payload

    monkeypatch.setattr(
        relay_service.transformer, "transform_payload", fake_transform_payload
    )

    response = httpx.Response(
        200,
        headers={"content-type": "application/json"},
        json={"response": "Use a cleanser.", "status": "ok"},
    )

    body = await relay_service._transform_backend_response(response)

    assert json.loads(body) == {
        "response": "Clara says to use a gentle cleanser.",
        "status": "ok",
    }


@pytest.mark.asyncio
async def test_transform_backend_response_plain_text(monkeypatch):
    async def fake_transform(text):
        return f"rewritten: {text}"

    monkeypatch.setattr(relay_service.transformer, "transform", fake_transform)

    response = httpx.Response(
        200,
        headers={"content-type": "text/plain"},
        content=b"Try a bland moisturizer.",
    )

    body = await relay_service._transform_backend_response(response)

    assert body == b"rewritten: Try a bland moisturizer."
