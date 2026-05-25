from typing import Any, Optional
from config import settings

try:
    from anthropic import AsyncAnthropic  # type: ignore
    HAS_ANTHROPIC = True
except Exception:  # pragma: no cover
    HAS_ANTHROPIC = False


class AnthropicClient:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        
        self.sdk_client: Optional[Any] = None
        if HAS_ANTHROPIC and self.api_key:
            self.sdk_client = AsyncAnthropic(api_key=self.api_key)

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
        Generates a response from Anthropic using the official SDK.
        """
        if not self.api_key or self.sdk_client is None:
            return text

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
