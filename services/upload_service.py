import httpx
from fastapi import HTTPException, status, UploadFile
from typing import List

from config import settings
from constants import DEFAULT_TIMEOUT, HEADER_X_API_KEY

http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)


async def forward_upload_request(files: List[UploadFile]) -> tuple[dict, int]:
    """
    Forwards file uploads to clintel's /upload/v2 endpoint.
    """
    headers = {
        HEADER_X_API_KEY: settings.CLINTEL_BACKEND_X_API_KEY,
    }

    # Prepare files for httpx
    # httpx expects files as a list of tuples: ("field_name", (filename, content, content_type))
    files_payload = []
    for file in files:
        content = await file.read()
        files_payload.append(("files", (file.filename, content, file.content_type)))

    try:
        response = await http_client.post(
            f"{settings.CLINTEL_BACKEND_URL.rstrip('/')}/upload/v2",
            files=files_payload,
            headers=headers,
        )
        return response.json(), response.status_code

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with clintel backend during upload: {str(e)}",
        )
