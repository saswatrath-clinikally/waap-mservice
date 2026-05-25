#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${OTHER_BACKEND_URL:-http://localhost:8080}"
API_KEY="${OTHER_BACKEND_API_KEY:-dermagptsecretkey123#}"
PAYLOAD='{"message":"Can I use niacinamide on my face to treat acne?"}'

RAW_RESPONSE="$(
  curl -sS --fail-with-body \
    -X POST "${BACKEND_URL}/chat" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: ${API_KEY}" \
    --data "${PAYLOAD}"
)"

RAW_RESPONSE="${RAW_RESPONSE}" poetry run python - <<'PY'
import asyncio
import json
import os
from typing import Any

from agents import transformer


def find_assistant_text(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in (
            "assistant",
            "assistant_message",
            "assistant_reply",
            "reply",
            "response",
            "output",
            "message",
            "text",
            "content",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, dict) or isinstance(value, list):
                nested = find_assistant_text(value)
                if nested:
                    return nested

        if "choices" in payload and isinstance(payload["choices"], list):
            for choice in payload["choices"]:
                nested = find_assistant_text(choice)
                if nested:
                    return nested

        for value in payload.values():
            nested = find_assistant_text(value)
            if nested:
                return nested

    if isinstance(payload, list):
        for item in payload:
            nested = find_assistant_text(item)
            if nested:
                return nested

    if isinstance(payload, str) and payload.strip():
        return payload

    return None


async def main() -> None:
    raw_response = os.environ["RAW_RESPONSE"]

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        parsed = raw_response

    assistant_text = find_assistant_text(parsed)
    if assistant_text is None:
        print("Could not locate an assistant message in the 8080 response.")
        print("Raw response:")
        print(raw_response)
        return

    transformed_text = await transformer.transform(assistant_text)
    print(transformed_text)


asyncio.run(main())
PY
