import logging
from clients.bigquery_client import get_bigquery_client

logger = logging.getLogger(__name__)

async def fetch_conversation_phone_numbers() -> list[str]:
    """
    Fetches the list of phone numbers by delegating to the BigQuery Client singleton.
    """
    bq_client = get_bigquery_client()
    return await bq_client.fetch_phone_numbers()
