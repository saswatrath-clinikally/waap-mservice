from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from constants import AgentType, ImageCategory


class ChatRequest(BaseModel):
    """Schema for incoming requests to the middleware proxy"""

    message: str = Field(..., description="The user message")
    thread_id: Optional[str] = Field(None, description="Optional thread identifier")
    file_urls: Optional[List[str]] = Field(
        None, description="Optional list of file URLs"
    )
    image_category: Optional[ImageCategory] = Field(
        None, description="Optional category for image processing"
    )

    # Using Any to catch any additional arbitrary payload fields sent by external service
    model_config = {"extra": "allow"}


class ChatResponse(BaseModel):
    """Schema for outgoing responses from the middleware proxy"""

    response: str = Field(..., description="The assistant's response")
    thread_id: str = Field(..., description="The thread identifier")
    trace_id: Optional[str] = Field(None, description="Optional trace identifier")
    agent_type: Optional[AgentType] = Field(
        None, description="Optional agent type from backend"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Context returned from backend"
    )
    model_config = {"extra": "allow"}
