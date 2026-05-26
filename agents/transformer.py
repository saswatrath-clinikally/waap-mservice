from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings
from prompts.agents.transformer import TRANSFORMER_SYSTEM_PROMPT
from clients.anthropic_client import AnthropicClient


@dataclass
class TransformerAgent:
    def __post_init__(self):
        self.client = AnthropicClient()

    async def transform(self, text: str) -> str:
        if not text.strip():
            return text

        if not settings.ANTHROPIC_API_KEY:
            return text

        return str(await self.client.generate_response(text, TRANSFORMER_SYSTEM_PROMPT))

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


transformer = TransformerAgent()
