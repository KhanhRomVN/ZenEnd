import json
import time
import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers


class DebugRequestMiddleware(BaseHTTPMiddleware):
    """Middleware để log toàn bộ request details"""
    
    async def dispatch(self, request: Request, call_next):
        # Chỉ log khi KHÔNG phải production (Render)
        is_production = os.getenv("RENDER") is not None
        
        # CRITICAL FIX: Skip middleware hoàn toàn trên production
        if is_production:
            return await call_next(request)
        
        # Log request details (chỉ local development)
        if request.url.path == "/v1/chat/completions":
            # CRITICAL: Clone body thay vì consume
            body_bytes = b""
            chunks = []
            
            async for chunk in request.stream():
                chunks.append(chunk)
                body_bytes += chunk
            
            if body_bytes:
                try:
                    body_json = json.loads(body_bytes.decode('utf-8'))
                    
                    messages = body_json.get("messages", [])
                    if messages:
                        system_messages = [msg for msg in messages if msg.get("role") == "system"]
                        user_messages = [msg for msg in messages if msg.get("role") == "user"]
                        
                        if system_messages:
                            for idx, msg in enumerate(system_messages):
                                content = msg.get("content", "")
                                content_length = len(content)
                                
                                try:
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
                        
                        if user_messages:
                            for idx, msg in enumerate(user_messages):
                                content = msg.get("content", "")
                                
                                if isinstance(content, list):
                                    extracted_texts = []
                                    image_count = 0
                                    
                                    for item in content:
                                        if isinstance(item, dict):
                                            if item.get("type") == "text":
                                                extracted_texts.append(item.get("text", ""))
                                            elif item.get("type") == "image":
                                                extracted_texts.append("[IMAGE]")
                                                image_count += 1
                                            elif item.get("type") == "image_url":
                                                image_url = item.get("image_url", {})
                                                if isinstance(image_url, dict):
                                                    url = image_url.get("url", "")
                                                elif isinstance(image_url, str):
                                                    url = image_url
                                                else:
                                                    url = ""
                                                
                                                if url.startswith("data:image"):
                                                    extracted_texts.append(f"[IMAGE_URL_{image_count}]")
                                                    
                                                    try:
                                                        import base64
                                                        import re
                                                        
                                                        match = re.match(r'data:image/([a-zA-Z]+);base64,(.+)', url)
                                                        if match:
                                                            image_format = match.group(1)
                                                            base64_data = match.group(2)
                                                            
                                                            image_bytes = base64.b64decode(base64_data)
                                                            
                                                            log_dir = "logs/images"
                                                            os.makedirs(log_dir, exist_ok=True)
                                                            
                                                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                                                            filename = f"{log_dir}/image_{timestamp}_{idx}_{image_count}.{image_format}"
                                                            
                                                            with open(filename, 'wb') as f:
                                                                f.write(image_bytes)
                                                            
                                                            print(f"[Middleware]   📸 Saved image: {filename} ({len(image_bytes)} bytes, format: {image_format})")
                                                            
                                                            image_count += 1
                                                        else:
                                                            print(f"[Middleware]   ⚠️ Could not parse image data URL")
                                                    
                                                    except Exception as save_error:
                                                        print(f"[Middleware]   ❌ Failed to save image: {save_error}")
                                                else:
                                                    extracted_texts.append(f"[IMAGE_URL_{image_count} - External URL]")
                                                    print(f"[Middleware]   🔗 External image URL detected: {url[:100]}...")
                                                    image_count += 1
                                    
                                    if image_count > 0:
                                        print(f"[Middleware]   🖼️ User message #{idx} contains {image_count} image(s)")
                                
                except Exception as e:
                    print(f"[Middleware]   - Parse error: {e}")
            
            # CRITICAL FIX: Tạo lại request với body stream mới - PROPER WAY
            chunk_index = 0
            
            async def new_receive():
                nonlocal chunk_index
                if chunk_index < len(chunks):
                    chunk = chunks[chunk_index]
                    chunk_index += 1
                    return {
                        "type": "http.request",
                        "body": chunk,
                        "more_body": chunk_index < len(chunks)
                    }
                else:
                    # End of stream
                    return {
                        "type": "http.request",
                        "body": b"",
                        "more_body": False
                    }
            
            # Replace request stream
            request._receive = new_receive
        
        response = await call_next(request)
        return response