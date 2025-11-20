"""
Parse response từ DeepSeek sang OpenAI format
"""
import json
import re
import time
import uuid

def parse_deepseek_response(response_text: str) -> dict:
    """
    Parse response từ ZenTab - Rebuild đơn giản thay vì parse phức tạp.
    ZenTab trả về JSON, ta chỉ cần parse 1 lần và rebuild.
    """
    
    if not response_text or not isinstance(response_text, str):
        return _create_fallback_response("Empty response from DeepSeek")
    
    cleaned_text = response_text.strip()
    
    if not cleaned_text:
        return _create_fallback_response("Empty response from DeepSeek")
    
    # Parse JSON (chỉ 1 lần)
    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        return _create_fallback_response(f"Invalid JSON from DeepSeek: {str(e)}")
    
    if not isinstance(parsed, dict):
        return _create_fallback_response("Response is not a JSON object")
    
    # Rebuild response từ parsed data
    response_id = parsed.get('id', f'chatcmpl-{uuid.uuid4().hex[:16]}')
    object_type = parsed.get('object', 'chat.completion.chunk')
    created = parsed.get('created', int(time.time()))
    model = parsed.get('model', 'deepseek-chat')
    system_fingerprint = parsed.get('system_fingerprint', f'fp_{uuid.uuid4().hex[:8]}')
    
    # Extract choices
    original_choices = parsed.get('choices', [])
    if not original_choices or len(original_choices) == 0:
        return _create_fallback_response("No choices in response")
    
    # Extract first choice
    original_choice = original_choices[0]
    choice_index = original_choice.get('index', 0)
    finish_reason = original_choice.get('finish_reason', 'stop')
    logprobs = original_choice.get('logprobs', None)
    
    # Extract message/delta
    message_data = original_choice.get('message') or original_choice.get('delta', {})
    role = message_data.get('role', 'assistant')
    content = message_data.get('content', '')
    tool_calls = message_data.get('tool_calls', None)
    
    # Extract usage
    original_usage = parsed.get('usage', {})
    prompt_tokens = original_usage.get('prompt_tokens', 0)
    completion_tokens = original_usage.get('completion_tokens', 0)
    total_tokens = original_usage.get('total_tokens', 0)
    
    # Rebuild clean response
    clean_response = {
        'id': response_id,
        'object': object_type,
        'created': created,
        'model': model,
        'choices': [{
            'index': choice_index,
            'finish_reason': finish_reason,
            'logprobs': logprobs,
            'message': {
                'role': role,
                'content': content,
                'tool_calls': tool_calls
            }
        }],
        'usage': {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        },
        'system_fingerprint': system_fingerprint
    }
    
    return clean_response

def convert_deepseek_to_openai(deepseek_data: dict) -> dict:
    result = deepseek_data.copy()
    result["model"] = "deepseek-chat"
    return result

def _create_fallback_response(response_text: str) -> dict:
    actual_content = response_text[:2000]
    
    try:
        if "content" in response_text and "message" in response_text:
            content_match = re.search(r'"content":\s*"([^"]+)"', response_text)
            if content_match:
                actual_content = content_match.group(1)
                actual_content = actual_content.replace('\\"', '"').replace('\\n', '\n')
    except Exception:
        pass
    
    fallback = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": actual_content
            },
            "finish_reason": "stop",
            "logprobs": None
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(response_text.split())
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }
    
    return fallback