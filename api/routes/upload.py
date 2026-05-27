from fastapi import APIRouter, UploadFile, File, Response
from typing import List

from services.upload_service import forward_upload_request

router = APIRouter()


@router.post("/upload")
async def upload_endpoint(
    response: Response,
    files: List[UploadFile] = File(...),
):
    """
    Acts as a pass-through proxy for the file upload endpoint.
    Receives multipart/form-data from Express -> Forwards to clintel /upload/v2 -> Returns response.
    """
    json_response, status_code = await forward_upload_request(files)

    response.status_code = status_code
    return json_response
