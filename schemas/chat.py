from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Schema for incoming requests to the middleware proxy"""

    message: str = Field(..., description="The user message")
    thread_id: Optional[str] = Field(None, description="Optional thread identifier")
    # Using Any to catch any additional arbitrary payload fields sent by external service
    model_config = {"extra": "allow"}


class ChatResponse(BaseModel):
    """Schema for outgoing responses from the middleware proxy"""

    response: str = Field(..., description="The assistant's response")
    status: Optional[str] = Field(None, description="Status of the request")
    model_config = {"extra": "allow"}
