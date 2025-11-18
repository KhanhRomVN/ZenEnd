"""
Fake response generator cho testing
"""
import uuid
import time


def create_fake_response(model: str = "deepseek-chat") -> dict:
    """
    Tạo fake response để test backend mà không cần gọi DeepSeek thực sự
    """
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Đây là fake response để test. Backend đang ở chế độ mock, không gọi DeepSeek thực sự."
            },
            "finish_reason": "stop",
            "logprobs": None
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }


def is_fake_mode_enabled() -> bool:
    """
    Kiểm tra có bật fake mode không
    Có thể thay đổi logic này để enable/disable qua env var
    """
    # TODO: Đọc từ environment variable hoặc config
    # import os
    # return os.getenv("FAKE_MODE", "false").lower() == "true"
    
    return True  # Hiện tại đang bật fake mode