"""
Parse response từ DeepSeek sang OpenAI format
"""
import json
import re
import time
import uuid

def parse_deepseek_response(response_text: str) -> dict:
    if response_text and isinstance(response_text, str):
        if response_text.startswith('"') and response_text.endswith('"'):
            try:
                first_decode = json.loads(response_text)
                
                if isinstance(first_decode, str):
                    second_decode = json.loads(first_decode)
                    
                    if isinstance(second_decode, dict) and all(key in second_decode for key in ['id', 'object', 'created', 'model', 'choices']):
                        if second_decode.get('object') == 'chat.completion.chunk':
                            second_decode = _convert_chunk_to_completion(second_decode)
                        return second_decode
                else:
                    response_text = json.dumps(first_decode)
            except json.JSONDecodeError:
                pass
        
        try:
            parsed = json.loads(response_text)
            
            if isinstance(parsed, dict):
                if all(key in parsed for key in ['id', 'object', 'created', 'model', 'choices']):
                    if parsed.get('object') == 'chat.completion.chunk':
                        parsed = _convert_chunk_to_completion(parsed)
                    return parsed
        except json.JSONDecodeError:
            pass
    
    if not response_text or response_text.strip() == "":
        return _create_fallback_response("The model returned an empty response. Please try again.")
    
    cleaned_text = response_text.strip()
    
    try:
        parsed_json = json.loads(cleaned_text, strict=False)
        
        if isinstance(parsed_json, dict):
            required_keys = ['id', 'object', 'created', 'model', 'choices']
            has_required = all(key in parsed_json for key in required_keys)
            
            if has_required:
                if parsed_json.get('object') == 'chat.completion.chunk':
                    choices = parsed_json.get('choices', [])
                    if choices and 'delta' in choices[0]:
                        delta = choices[0]['delta']
                        choices[0]['message'] = {
                            'role': delta.get('role', 'assistant'),
                            'content': delta.get('content', '')
                        }
                        del choices[0]['delta']
                        parsed_json['object'] = 'chat.completion'
                
                return parsed_json
    except json.JSONDecodeError:
        try:
            import re
            
            def fix_unescaped_quotes(match):
                field_name = match.group(1)
                content = match.group(2)
                fixed_content = content.replace('"', '\\"')
                return f'"{field_name}": "{fixed_content}"'
            
            fixed_text = re.sub(
                r'"(content)":\s*"([^"]*(?:"[^"]*)*)"',
                lambda m: f'"{m.group(1)}": "{m.group(2).replace(chr(34), chr(92) + chr(34))}"',
                cleaned_text
            )
            
            parsed_json = json.loads(fixed_text, strict=False)
            
            if isinstance(parsed_json, dict) and all(key in parsed_json for key in ['id', 'object', 'created', 'model', 'choices']):
                if parsed_json.get('object') == 'chat.completion.chunk':
                    choices = parsed_json.get('choices', [])
                    if choices and 'delta' in choices[0]:
                        delta = choices[0]['delta']
                        choices[0]['message'] = {
                            'role': delta.get('role', 'assistant'),
                            'content': delta.get('content', '')
                        }
                        del choices[0]['delta']
                        parsed_json['object'] = 'chat.completion'
                
                return parsed_json
        except Exception:
            pass
    
    prefixes_to_remove = ["xmlCopy", "xml", "Copy"]
    for prefix in prefixes_to_remove:
        if cleaned_text.startswith(prefix):
            cleaned_text = cleaned_text[len(prefix):].strip()
    
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r'^```(?:xml)?\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
    
    if cleaned_text.startswith('"') and cleaned_text.endswith('"'):
        try:
            fixed_text = cleaned_text[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            parsed_inner = json.loads(fixed_text)
            if isinstance(parsed_inner, dict) and all(key in parsed_inner for key in ['id', 'object', 'created', 'model', 'choices']):
                return parsed_inner
        except Exception:
            pass
    
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

def _convert_chunk_to_completion(chunk_data: dict) -> dict:
    completion_data = chunk_data.copy()
    completion_data['object'] = 'chat.completion'
    
    choices = completion_data.get('choices', [])
    for choice in choices:
        if 'delta' in choice:
            delta = choice['delta']
            choice['message'] = {
                'role': delta.get('role', 'assistant'),
                'content': delta.get('content', '')
            }
            del choice['delta']
    
    return completion_data