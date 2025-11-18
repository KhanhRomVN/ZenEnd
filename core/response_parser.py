"""
Parse response từ DeepSeek sang OpenAI format
"""
import json
import re
import time
import uuid


def parse_deepseek_response(response_text: str) -> dict:
    """
    Parse response từ DeepSeek web format sang OpenAI format
    """
    try:
        # Thử parse trực tiếp nếu đã là JSON
        data = json.loads(response_text)
        
        # Nếu đã đúng format DeepSeek, convert sang OpenAI format
        if "id" in data and "choices" in data:
            return convert_deepseek_to_openai(data)
        
    except json.JSONDecodeError:
        # Không phải JSON thuần, tìm JSON trong text
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return convert_deepseek_to_openai(data)
            except:
                pass
    
    # Fallback: wrap text thành OpenAI format
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_text
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }


def convert_deepseek_to_openai(deepseek_data: dict) -> dict:
    """
    Convert từ DeepSeek web format sang OpenAI API format
    """
    # DeepSeek format thường giống OpenAI, chỉ cần đổi model name
    result = deepseek_data.copy()
    result["model"] = "deepseek-chat"
    return result