import httpx
from typing import Any
from config import settings
from constants import DEFAULT_TIMEOUT, HEADER_CONTENT_TYPE, CONTENT_TYPE_JSON

try:
    from anthropic import AsyncAnthropic  # type: ignore
except Exception:  # pragma: no cover
    AsyncAnthropic = None


class AnthropicClient:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.base_url = settings.ANTHROPIC_BASE_URL.rstrip("/")
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS

        if AsyncAnthropic is not None and self.api_key:
            self.sdk_client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.sdk_client = None

    def _extract_text_blocks(self, response_payload: Any) -> str:
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

    async def generate_response(self, text: str, system_prompt: str) -> str:
        """
        Generates a response from Anthropic, falling back to HTTP if SDK is missing.
        """
        if not self.api_key:
            return text

        if self.sdk_client is not None:
            return await self._generate_with_sdk(text, system_prompt)

        return await self._generate_with_http(text, system_prompt)

    async def _generate_with_sdk(self, text: str, system_prompt: str) -> str:
        response = await self.sdk_client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        )
        transformed = self._extract_text_blocks(response.model_dump())
        return transformed or text

    async def _generate_with_http(self, text: str, system_prompt: str) -> str:
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
        }
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
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
            transformed = self._extract_text_blocks(response.json())
            return transformed or text
