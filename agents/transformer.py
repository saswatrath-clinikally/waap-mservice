from __future__ import annotations

import json
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
            raw_text = payload["response"]

            # The clintel backend sometimes wraps its response in a double-encoded JSON string
            # e.g. "response": "{\n  \"message\": \"...\",\n  \"products\": []}"
            # We must detect this, unpack it, transform ONLY the text message, and repackage it.
            try:
                nested_json = json.loads(raw_text)
                if isinstance(nested_json, dict):
                    # Check for "response" or "message" key in the nested JSON
                    target_key = (
                        "response"
                        if "response" in nested_json
                        else "message"
                        if "message" in nested_json
                        else None
                    )

                    if (
                        target_key
                        and isinstance(nested_json[target_key], str)
                        and nested_json[target_key].strip()
                    ):
                        # Transform just the text inside the nested JSON
                        transformed_text = await self.transform(nested_json[target_key])
                        nested_json[target_key] = transformed_text
                        # Repackage the JSON exactly as clintel sent it
                        payload["response"] = json.dumps(
                            nested_json, ensure_ascii=False
                        )
                        return payload
            except Exception:
                pass

            # If it wasn't a nested JSON string, transform the raw text directly
            if raw_text.strip():
                transformed = await self.transform(raw_text)
                payload["response"] = transformed

        return payload


transformer = TransformerAgent()
