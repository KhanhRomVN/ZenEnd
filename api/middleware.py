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
                    
                    # 🆕 LOG: Tách system prompt và user messages
                    messages = body_json.get("messages", [])
                    if messages:
                        system_messages = [msg for msg in messages if msg.get("role") == "system"]
                        user_messages = [msg for msg in messages if msg.get("role") == "user"]
                        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
                        
                        # 🔥 LOG SYSTEM PROMPT (cực dài)
                        if system_messages:
                            for idx, msg in enumerate(system_messages):
                                content = msg.get("content", "")
                                content_length = len(content)
                                
                                # 💾 Lưu system prompt vào file để phân tích sau
                                try:
                                    import os
                                    import time
                                    
                                    log_dir = "logs/system_prompts"
                                    os.makedirs(log_dir, exist_ok=True)
                                    
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    filename = f"{log_dir}/system_prompt_{timestamp}.txt"
                                    
                                    with open(filename, 'w', encoding='utf-8') as f:
                                        f.write(f"Timestamp: {timestamp}\n")
                                        f.write(f"Length: {content_length} chars\n")
                                        f.write(f"Estimated tokens: ~{content_length // 4}\n")
                                        f.write(f"\n{'='*80}\n\n")
                                        f.write(content)
                                    
                                except Exception as save_error:
                                    print(f"[ERROR] Failed to save system prompt: {save_error}")
                        
                        # 🆕 LOG USER MESSAGES
                        if user_messages:
                            
                            for idx, msg in enumerate(user_messages):
                                content = msg.get("content", "")
                                
                                # Xử lý content dạng array hoặc string
                                if isinstance(content, list):
                                    extracted_texts = []
                                    for item in content:
                                        if isinstance(item, dict):
                                            if item.get("type") == "text":
                                                extracted_texts.append(item.get("text", ""))
                                            elif item.get("type") == "image":
                                                extracted_texts.append("[IMAGE]")
                                    
                                    full_content = "\n".join(extracted_texts)
                                else:
                                    full_content = content
                                
                                # Preview (200 chars đầu)
                                if len(full_content) > 200:
                                    content_preview = full_content[:200] + "..."
                                else:
                                    content_preview = full_content
                                                
                except Exception as e:
                    print(f"[Middleware]   - Parse error: {e}")
                
                # QUAN TRỌNG: Tạo lại request với body đã đọc
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
        
        response = await call_next(request)
        return response