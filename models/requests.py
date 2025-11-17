"""
Pydantic models cho HTTP requests
"""
from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]