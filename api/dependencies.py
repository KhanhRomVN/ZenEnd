"""
API dependencies - Authentication
"""
from typing import Optional
from fastapi import Header, HTTPException

from config.settings import API_KEY


async def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Validate API key từ Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid Authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token