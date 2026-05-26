#!/usr/bin/env bash
set -euo pipefail

# This script hits the clintel backend directly to get a raw response, 
# and then runs it through our transformer to test the tone rewrite.

BACKEND_URL="${CLINTEL_BACKEND_URL:-http://localhost:8080}"
API_KEY="${CLINTEL_BACKEND_X_API_KEY:-}"

# The question you want to test
QUESTION="Can I use niacinamide on my face to treat acne?"

PAYLOAD=$(cat <<EOF
{
  "message": "$QUESTION"
}
EOF
)

echo "Hitting clintel backend with question: '$QUESTION'"

RAW_RESPONSE="$(
  curl -sS --fail-with-body \
    -X POST "${BACKEND_URL}/api/routes/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    --data "${PAYLOAD}"
)"

echo "--------------------------------------------------"
echo "RAW RESPONSE FROM CLINTEL:"
echo "$RAW_RESPONSE"
echo "--------------------------------------------------"
echo "TRANSFORMING RESPONSE (Applying Clara Persona)..."
echo "--------------------------------------------------"

RAW_RESPONSE="${RAW_RESPONSE}" poetry run python - <<'PY'
import asyncio
import json
import os
import sys
from typing import Any

from agents.transformer import transformer

async def main() -> None:
    raw_response = os.environ.get("RAW_RESPONSE", "")
    if not raw_response:
        print("No raw response received.")
        sys.exit(1)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        parsed = raw_response

    # Test the full payload transformation logic
    transformed_payload = await transformer.transform_payload(parsed)
    
    print(json.dumps(transformed_payload, indent=2, ensure_ascii=False))

asyncio.run(main())
PY
