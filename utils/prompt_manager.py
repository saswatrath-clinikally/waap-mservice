"""
Simplified Prompt Manager.
Supports local prompts for development/production environments.
"""

import logging
from typing import Dict, Any, Optional
from utils.local_prompt_loader import get_local_prompt_loader

logger = logging.getLogger(__name__)


class PromptManager:
    """Simple wrapper for prompt management."""

    def __init__(self):
        """Initialize local prompt loader."""
        self.local_loader = get_local_prompt_loader()
        logger.info("Local prompt loader initialized")

    def get_prompt(self, name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Get compiled prompt.

        Args:
            name: Prompt name (from PromptNames enum)
            variables: Variables to compile into the prompt

        Returns:
            Compiled prompt string
        """
        try:
            compiled = str(self.local_loader.get_prompt(name, variables))
            logger.debug(f"Retrieved prompt '{name}' from local files")
            return compiled
        except Exception as e:
            logger.error(f"Failed to get prompt '{name}' from local files: {e}")
            raise


# Singleton instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get or create the prompt manager singleton."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def reset_prompt_manager() -> None:
    """Reset the prompt manager singleton (useful for testing)."""
    global _prompt_manager
    _prompt_manager = None
