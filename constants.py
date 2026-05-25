from enum import Enum


class PromptNames(str, Enum):
    """Prompt names used throughout the application."""

    TRANSFORMER = "agents/transformer"


# API Constants
DEFAULT_TIMEOUT: float = 60.0
HTTP_400_BAD_REQUEST: int = 400
HTTP_502_BAD_GATEWAY: int = 502

# Anthropic Defaults
DEFAULT_ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
DEFAULT_ANTHROPIC_MAX_TOKENS: int = 512

# Headers
HEADER_CONTENT_TYPE: str = "Content-Type"
HEADER_X_API_KEY: str = "X-Api-Key"
CONTENT_TYPE_JSON: str = "application/json"
