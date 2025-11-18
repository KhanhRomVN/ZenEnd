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
                    
                    # 🆕 LOG: Hiển thị prompt từ Cline
                    messages = body_json.get("messages", [])
                    if messages:
                        print(f"\n{'='*60}")
                        print(f"[Middleware] 📨 CLINE REQUEST")
                        print(f"{'='*60}")
                        print(f"Model: {body_json.get('model', 'N/A')}")
                        print(f"Total messages: {len(messages)}")
                        print(f"\n--- MESSAGES ---")
                        for idx, msg in enumerate(messages):
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")
                            
                            # Xử lý content dạng array hoặc string
                            if isinstance(content, list):
                                # Extract text từ array
                                extracted_texts = []
                                for item in content:
                                    if isinstance(item, dict):
                                        if item.get("type") == "text":
                                            extracted_texts.append(item.get("text", ""))
                                        elif item.get("type") == "image":
                                            extracted_texts.append("[IMAGE]")
                                
                                full_content = "\n".join(extracted_texts)
                                if len(full_content) > 200:
                                    content_preview = full_content[:200] + "..."
                                else:
                                    content_preview = full_content
                            else:
                                if len(content) > 200:
                                    content_preview = content[:200] + "..."
                                else:
                                    content_preview = content
                            
                            print(f"\n[{idx+1}] Role: {role}")
                            print(f"Content: {content_preview}")
                        print(f"\n{'='*60}\n")
                    
                except Exception as e:
                    print(f"[Middleware]   - Parse error: {e}")
                
                # QUAN TRỌNG: Tạo lại request với body đã đọc
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
        
        response = await call_next(request)
        return response