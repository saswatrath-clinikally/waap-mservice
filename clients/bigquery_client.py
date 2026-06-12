import os
import json
import base64
import logging
import asyncio
from typing import Optional, List
from google.cloud import bigquery

from config import settings

logger = logging.getLogger(__name__)

class BigQueryClient:
    """Client for interacting with BigQuery, mirroring clintel's approach."""
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: str = "clintel_traces"):
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.dataset_id = dataset_id
        
        # Setup authentication using clintel's method
        self._setup_authentication()
        
        if self.project_id:
            try:
                self.client = bigquery.Client(project=self.project_id)
            except Exception as e:
                logger.error(f"Failed to initialize BigQuery client: {e}")
                self.client = None
        else:
            logger.warning("GCP_PROJECT_ID not set. BigQuery client disabled.")
            self.client = None
            
        self.conversations_table = f"{self.project_id}.{self.dataset_id}.conversations"
        
    def _setup_authentication(self) -> None:
        """
        Setup Google Cloud authentication from environment variable.
        This exact approach is used in clintel to write the key to a temp file.
        """
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return
            
        encoded_key = settings.BIGQUERY_SERVICE_ACCOUNT_KEY
        if encoded_key:
            try:
                # Handle both base64 and raw JSON formats
                try:
                    decoded_key = base64.b64decode(encoded_key)
                    # Validate it's valid JSON
                    json.loads(decoded_key)
                except Exception:
                    # Fallback to treating it as direct string
                    decoded_key = encoded_key.encode('utf-8')
                    
                # Write to temp file (clintel standard)
                temp_path = "/tmp/bigquery-key.json"
                with open(temp_path, "wb") as f:
                    f.write(decoded_key)
                    
                # Set environment variable for Google SDK
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
                return
            except Exception as e:
                logger.error(f"Failed to process BIGQUERY_SERVICE_ACCOUNT_KEY: {e}")

    async def fetch_phone_numbers(self) -> List[str]:
        """Fetch distinct phone numbers using asyncio executor to avoid blocking main thread."""
        if not self.client:
            logger.warning("Cannot fetch numbers - BigQuery client is not initialized")
            return []
            
        try:
            query = f"SELECT DISTINCT phone_number FROM `{self.conversations_table}` WHERE phone_number IS NOT NULL"
            
            # Use run_in_executor to avoid blocking the event loop (clintel best practice)
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.query(query).result()
            )
            
            phone_numbers = [row.phone_number for row in results]
            return phone_numbers
            
        except Exception as e:
            logger.error(f"Error fetching data from BigQuery: {e}")
            return []

# Singleton instance
_bigquery_client: Optional[BigQueryClient] = None

def get_bigquery_client() -> BigQueryClient:
    """Get or create BigQuery client singleton."""
    global _bigquery_client
    if _bigquery_client is None:
        _bigquery_client = BigQueryClient()
    return _bigquery_client
