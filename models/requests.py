"""
Pydantic models cho HTTP requests
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


from typing import Union, List

class Message(BaseModel):
    role: str
    content: Union[str, List[dict]]  # 🆕 Hỗ trợ cả string và array
    
    class Config:
        extra = "allow"  # Cho phép fields như name, function_call, etc.


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=1024)
    top_p: Optional[float] = Field(default=1.0)
    stream: Optional[bool] = Field(default=False)
    stop: Optional[Any] = Field(default=None)
    n: Optional[int] = Field(default=1)
    presence_penalty: Optional[float] = Field(default=0.0)
    frequency_penalty: Optional[float] = Field(default=0.0)
    
    class Config:
        extra = "allow"  # Cho phép các field không khai báo (như logprobs, user, etc.)