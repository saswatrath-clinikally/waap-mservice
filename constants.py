from enum import Enum


class PromptNames(str, Enum):
    """Prompt names used throughout the application."""

    TRANSFORMER = "agents/transformer"


class ModelName(str, Enum):
    """AI model names used in the system."""

    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    CLAUDE_HAIKU_4_5 = "claude-haiku-4-5-20251001"


# API Constants
DEFAULT_TIMEOUT: float = 60.0

# Anthropic Defaults
DEFAULT_ANTHROPIC_MAX_TOKENS: int = 512

# Headers
HEADER_CONTENT_TYPE: str = "Content-Type"
HEADER_X_API_KEY: str = "X-Api-Key"
CONTENT_TYPE_JSON: str = "application/json"
