import os
from fastapi import Security
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

# Setting up the hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# This key secures our middleware endpoint from public access
HASHED_API_KEY = os.getenv("MIDDLEWARE_HASHED_API_KEY")


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verifies a plain-text API key against its hashed version."""
    return bool(pwd_context.verify(plain_api_key, hashed_api_key))


async def get_api_key(api_key: str = Security(api_key_header)) -> bool:
    """
    A dependency that checks for and validates the API key.
    Returns True if the API key is valid, False otherwise.
    """
    if not HASHED_API_KEY:
        # If no auth is configured, default to secure (block)
        return False

    if not api_key:
        return False

    return verify_api_key(api_key, HASHED_API_KEY)


def hash_api_key(plain_api_key: str) -> str:
    """Hashes a new API key for storage."""
    return str(pwd_context.hash(plain_api_key))
