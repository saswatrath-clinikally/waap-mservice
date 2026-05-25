from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings
from constants import PromptNames
from utils.prompt_manager import get_prompt_manager
from clients.anthropic_client import AnthropicClient


@dataclass
class TransformerAgent:
    def __post_init__(self):
        self.prompt_manager = get_prompt_manager()
        self.client = AnthropicClient()

    async def transform(self, text: str) -> str:
        if not text.strip():
            return text

        if not settings.ANTHROPIC_API_KEY:
            return text

        system_prompt = self.prompt_manager.get_prompt(PromptNames.TRANSFORMER)
        return str(await self.client.generate_response(text, system_prompt))

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
