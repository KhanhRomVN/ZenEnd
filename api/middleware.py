
import json
import time
import os
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
                                    image_count = 0
                                    
                                    for item in content:
                                        if isinstance(item, dict):
                                            if item.get("type") == "text":
                                                extracted_texts.append(item.get("text", ""))
                                            elif item.get("type") == "image":
                                                extracted_texts.append("[IMAGE]")
                                                image_count += 1
                                            elif item.get("type") == "image_url":
                                                # 🖼️ EXTRACT IMAGE DATA
                                                image_url = item.get("image_url", {})
                                                if isinstance(image_url, dict):
                                                    url = image_url.get("url", "")
                                                elif isinstance(image_url, str):
                                                    url = image_url
                                                else:
                                                    url = ""
                                                
                                                if url.startswith("data:image"):
                                                    extracted_texts.append(f"[IMAGE_URL_{image_count}]")
                                                    
                                                    # 💾 Lưu ảnh ra file để phân tích
                                                    try:
                                                        import base64
                                                        import re
                                                        
                                                        # Extract base64 data từ data URL
                                                        # Format: data:image/png;base64,iVBORw0KGgoAAAANS...
                                                        match = re.match(r'data:image/([a-zA-Z]+);base64,(.+)', url)
                                                        if match:
                                                            image_format = match.group(1)  # png, jpeg, etc.
                                                            base64_data = match.group(2)
                                                            
                                                            # Decode base64
                                                            image_bytes = base64.b64decode(base64_data)
                                                            
                                                            # Tạo thư mục lưu ảnh
                                                            log_dir = "logs/images"
                                                            os.makedirs(log_dir, exist_ok=True)
                                                            
                                                            # Tạo tên file unique
                                                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                                                            filename = f"{log_dir}/image_{timestamp}_{idx}_{image_count}.{image_format}"
                                                            
                                                            # Lưu ảnh
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
                                    
                                    full_content = "\n".join(extracted_texts)
                                    
                                    # Log summary nếu có ảnh
                                    if image_count > 0:
                                        print(f"[Middleware]   🖼️ User message #{idx} contains {image_count} image(s)")
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