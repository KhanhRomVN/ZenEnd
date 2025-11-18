"""
Parse response từ DeepSeek sang OpenAI format
"""
import json
import re
import time
import uuid

def parse_deepseek_response(response_text: str) -> dict:
    """
    Parse response từ DeepSeek (XML format) sang OpenAI format
    """
    if not response_text or response_text.strip() == "":
        return _create_fallback_response("The model returned an empty response. Please try again.")
    
    cleaned_text = response_text.strip()
    
    prefixes_to_remove = ["xmlCopy", "xml", "Copy"]
    for prefix in prefixes_to_remove:
        if cleaned_text.startswith(prefix):
            cleaned_text = cleaned_text[len(prefix):].strip()
    
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r'^```(?:xml)?\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
    
    from core.tool_parser import parse_xml_tools
    
    remaining_text, tool_calls = parse_xml_tools(cleaned_text)
    
    response_data = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": remaining_text.strip() if remaining_text else "",
                "tool_calls": tool_calls if tool_calls else None
            },
            "finish_reason": "tool_calls" if tool_calls else "stop",
            "logprobs": None
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(response_text.split())
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }
    
    if response_data["choices"][0]["message"]["tool_calls"] is None:
        del response_data["choices"][0]["message"]["tool_calls"]
    
    return response_data
    
    prefixes_to_remove = [
        "jsonCopyDownload",
        "jsonCopy",
        "json",
        "Copy",
        "Download"
    ]
    
    for prefix in prefixes_to_remove:
        if cleaned_text.startswith(prefix):
            cleaned_text = cleaned_text[len(prefix):].strip()
    
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r'^```(?:json)?\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
    
    try:
        data = json.loads(cleaned_text, strict=False)
        
        if "id" in data and "choices" in data:
            converted = convert_deepseek_to_openai(data)
            return converted
                
    except json.JSONDecodeError:
        try:
            fixed_text = cleaned_text
            
            def fix_nested_quotes(match):
                args_content = match.group(1)
                if args_content.startswith('{') and args_content.endswith('}'):
                    fixed = args_content.replace('"', '\\"')
                    return f'"arguments": "{fixed}"'
                return match.group(0)
            
            fixed_text = re.sub(r'"arguments":\s*"([^"]*\{[^}]*\}[^"]*)"', fix_nested_quotes, fixed_text)
            
            data = json.loads(fixed_text, strict=False)
            
            if "id" in data and "choices" in data:
                converted = convert_deepseek_to_openai(data)
                return converted
                
        except Exception:
            pass
        
        brace_count = 0
        start_idx = cleaned_text.find('{')
        
        if start_idx == -1:
            return _create_fallback_response(response_text)
        
        end_idx = start_idx
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(cleaned_text)):
            char = cleaned_text[i]
            
            if char == '"' and not escape_next:
                in_string = not in_string
            elif char == '\\':
                escape_next = not escape_next
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            escape_next = False
        
        if brace_count != 0:
            return _create_fallback_response(response_text)
        
        json_str = cleaned_text[start_idx:end_idx]
        
        try:
            data = json.loads(json_str, strict=False)
            converted = convert_deepseek_to_openai(data)
            return converted
        except Exception:
            return _create_fallback_response(response_text)
    
    return _create_fallback_response(response_text)


def convert_deepseek_to_openai(deepseek_data: dict) -> dict:
    """
    Convert từ DeepSeek web format sang OpenAI API format
    """
    result = deepseek_data.copy()
    result["model"] = "deepseek-chat"
    return result


def _create_fallback_response(response_text: str) -> dict:
    """
    Tạo fallback response khi không parse được JSON
    """
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