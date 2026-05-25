"""
Local prompt loader for fallback when external prompt manager is unavailable.
Loads prompts from the local codebase.
"""

import logging
from typing import Dict, Any, Optional
from constants import PromptNames

logger = logging.getLogger(__name__)


class LocalPromptLoader:
    """Loads prompts from local files in the prompts folder."""

    def __init__(self):
        """Initialize the prompt loader and load all prompts."""
        self.prompts_cache: Dict[str, str] = {}
        self._load_all_prompts()

    def _load_all_prompts(self) -> None:
        """Load all prompts from local files into cache."""
        try:
            # Import all prompt modules
            from prompts.agents import transformer

            # Map PromptNames to actual prompt strings
            self.prompts_cache = {
                PromptNames.TRANSFORMER: transformer.TRANSFORMER_SYSTEM_PROMPT,
            }
            logger.debug(f"Loaded {len(self.prompts_cache)} prompts into local cache")

        except Exception as e:
            logger.error(f"Failed to load local prompts: {e}")
            self.prompts_cache = {}

    def get_prompt(self, name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Get prompt by name from cache and format with variables."""
        if name not in self.prompts_cache:
            raise KeyError(f"Prompt '{name}' not found in local cache")

        prompt = self.prompts_cache[name]

        # Simple string formatting if variables are provided
        if variables:
            try:
                return prompt.format(**variables)
            except KeyError as e:
                logger.warning(f"Missing variable for prompt formatting: {e}")
                # Try partial formatting or return as is in real scenario
                return prompt

        return prompt


# Singleton instance
_local_loader: Optional[LocalPromptLoader] = None


def get_local_prompt_loader() -> LocalPromptLoader:
    """Get or create the local prompt loader singleton."""
    global _local_loader
    if _local_loader is None:
        _local_loader = LocalPromptLoader()
    return _local_loader
