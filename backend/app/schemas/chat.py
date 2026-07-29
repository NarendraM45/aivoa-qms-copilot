from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class ChatRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    message: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    role: str = "assistant"
    message: str
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
