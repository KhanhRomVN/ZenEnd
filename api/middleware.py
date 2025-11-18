"""
Custom middleware để log raw request body
"""
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class DebugRequestMiddleware(BaseHTTPMiddleware):
    """Middleware để log toàn bộ request details"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details
        if request.url.path == "/v1/chat/completions":
            # Đọc raw body
            body = await request.body()
            if body:
                try:
                    body_json = json.loads(body.decode('utf-8'))
                except Exception as e:
                    print(f"[Middleware]   - Parse error: {e}")
                
                # QUAN TRỌNG: Tạo lại request với body đã đọc
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
        
        response = await call_next(request)
        return response