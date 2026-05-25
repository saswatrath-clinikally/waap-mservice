import logging
from typing import Any, Optional
from config import settings
from constants import ModelName, DEFAULT_ANTHROPIC_MAX_TOKENS

try:
    from anthropic import AsyncAnthropic  # type: ignore

    HAS_ANTHROPIC = True
except Exception:  # pragma: no cover
    HAS_ANTHROPIC = False

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self):
        """
        Initialize the Anthropic client using centralized configuration.
        """
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = ModelName.CLAUDE_SONNET_4.value
        self.max_tokens = DEFAULT_ANTHROPIC_MAX_TOKENS

        self.sdk_client: Optional[Any] = None
        if HAS_ANTHROPIC and self.api_key:
            self.sdk_client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Anthropic SDK client initialized")
        else:
            logger.warning("Anthropic SDK is unavailable or API key is missing")

    def _extract_text_blocks(self, response_payload: Any) -> str:
        """
        Extract raw text strings from the Anthropic response structure.
        """
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
            logger.error(
                "Cannot generate response: Anthropic SDK is not properly initialized"
            )
            return text

        try:
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
        except Exception as e:
            logger.error(f"Anthropic API call failed: {str(e)}")
            return text
