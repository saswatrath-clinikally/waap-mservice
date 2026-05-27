from fastapi import APIRouter, Request, Response

from services.upload_service import forward_upload_request

router = APIRouter()


@router.post("/upload")
async def upload_endpoint(request: Request):
    """
    Acts as a raw network pass-through proxy for the file upload endpoint.
    Receives raw HTTP request from Express -> Forwards directly to clintel /upload/v2 -> Returns response.
    """
    content, status_code, media_type = await forward_upload_request(request)

    return Response(
        content=content,
        status_code=status_code,
        media_type=media_type,
    )
