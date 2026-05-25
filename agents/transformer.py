from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from constants import (
    DEFAULT_TIMEOUT,
    HEADER_CONTENT_TYPE,
    CONTENT_TYPE_JSON,
    PromptNames,
)
from config import settings
from utils.prompt_manager import get_prompt_manager

try:
    from anthropic import AsyncAnthropic  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AsyncAnthropic = None


def _extract_text_blocks(response_payload: Any) -> str:
    if not isinstance(response_payload, dict):
        return ""

    content = response_payload.get("content", [])
    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts).strip()


@dataclass
class TransformerAgent:
    def __post_init__(self):
        self.prompt_manager = get_prompt_manager()

    async def transform(self, text: str) -> str:
        if not text.strip():
            return text

        if not settings.ANTHROPIC_API_KEY:
            return text

        system_prompt = self.prompt_manager.get_prompt(PromptNames.TRANSFORMER)

        if AsyncAnthropic is not None:
            return await self._transform_with_sdk(text, system_prompt)

        return await self._transform_with_http(text, system_prompt)

    async def transform_payload(self, payload: Any) -> Any:
        # Based on the orchestrator backend, the assistant message is always in the "response" key.
        if (
            isinstance(payload, dict)
            and "response" in payload
            and isinstance(payload["response"], str)
        ):
            text = payload["response"]
            if text.strip():
                transformed = await self.transform(text)
                payload["response"] = transformed

        return payload

    async def _transform_with_sdk(self, text: str, system_prompt: str) -> str:
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        )
        transformed = _extract_text_blocks(response.model_dump())
        return transformed or text

    async def _transform_with_http(self, text: str, system_prompt: str) -> str:
        url = f"{settings.ANTHROPIC_BASE_URL.rstrip('/')}/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
        }
        payload = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": settings.ANTHROPIC_MAX_TOKENS,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            transformed = _extract_text_blocks(response.json())
            return transformed or text


transformer = TransformerAgent()
