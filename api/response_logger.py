"""
Middleware để log raw HTTP response body gửi tới Cline
"""
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
import io

def is_valid_json(json_str: str) -> bool:
    """
    Check if a string is valid JSON
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

class ResponseLoggerMiddleware(BaseHTTPMiddleware):
    """Log raw HTTP response - COMPLETE version"""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/v1/chat/completions":
            response = await call_next(request)
            
            # 🔧 FIX: Clone response body WITHOUT consuming original
            body_bytes = b""
            chunks = []
            
            async for chunk in response.body_iterator:
                chunks.append(chunk)
                body_bytes += chunk
            
            # 🔧 ENHANCED LOGGING: Log COMPLETE response
            try:
                body_json = json.loads(body_bytes.decode('utf-8'))

                # Log choices details
                choices = body_json.get('choices', [])
                
                for i, choice in enumerate(choices):
                    message = choice.get('message', {})                    
                    content = message.get('content')
                    tool_calls = message.get('tool_calls')
                    
                    if tool_calls:
                        args = tool.get('function', {}).get('arguments', '')
                
                # Log usage
                usage = body_json.get('usage', {})
                
                full_json = json.dumps(body_json, indent=2, ensure_ascii=False)
                                
                if choices:
                    choice = choices[0]
                    message = choice.get('message', {})
                    content = message.get('content')
                    tool_calls = message.get('tool_calls', [])
                    finish_reason = choice.get('finish_reason')
                    
                    # Check conditions that might cause EmptyAssistantMessage
                    conditions = {
                        "content_is_none": content is None,
                        "content_is_empty": content == "",
                        "has_tool_calls": bool(tool_calls),
                        "finish_reason_is_tool_calls": finish_reason == "tool_calls",
                        "content_has_meaningful_text": bool(content and content.strip() and content.strip() != "I understand. How can I help you with your project?"),
                        "tool_calls_have_valid_names": all(
                            tool.get('function', {}).get('name') and 
                            tool.get('function', {}).get('name') != "send_message"
                            for tool in tool_calls
                        ) if tool_calls else False
                    }
                
                # Check for common Cline issues in the raw JSON string
                body_str = body_bytes.decode('utf-8')
                issues = {
                    'empty_content': '"content":""' in body_str,
                    'null_content': '"content":null' in body_str,
                    'empty_tool_calls': '"tool_calls":[]' in body_str,
                    'null_tool_calls': '"tool_calls":null' in body_str,
                    'tool_calls_finish_with_empty_content': '"finish_reason":"tool_calls"' in body_str and ('"content":""' in body_str or '"content":null' in body_str),
                    'send_message_tool': '"name":"send_message"' in body_str
                }
                
                for issue, detected in issues.items():
                    status = "❌ DETECTED" if detected else "✅ OK"
            
            except Exception as e:
                print(f"[ResponseLogger] ❌ Error parsing response: {e}")
            
            # 🔧 CRITICAL: Return NEW response with ORIGINAL body
            async def new_body_iterator():
                for chunk in chunks:
                    yield chunk

            return Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # For other routes, just proceed normally
        return await call_next(request)