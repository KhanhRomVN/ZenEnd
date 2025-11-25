import time
import uuid
import json

ENABLE_FAKE_RESPONSE = False


def is_fake_mode_enabled() -> bool:
    return ENABLE_FAKE_RESPONSE


# ===== CUSTOM CONTENT =====
# 🎯 SỬA CONTENT Ở ĐÂY để test fake response
FAKE_CONTENT = """Tôi đã dừng server thành công. Bây giờ tôi sẽ cập nhật file cấu hình cline_mcp_settings.json để thêm MCP server filesystem.
<write_to_file>
<path>../../../.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
</path>
<content>
{
 "mcpServers": {
 "github.com/modelcontextprotocol/servers/tree/main/src/filesystem": {
 "command": "npx",
 "args": [
 "-y",
 "@modelcontextprotocol/server-filesystem",
 "/home/khanhromvn/Documents/Coding/ZenTab"
 ],
 "disabled": false,
 "autoApprove": []
 }
 }
}
</content>
<task_progress>
- [x] Tải tài liệu MCP
- [x] Đọc file cline_mcp_settings.json hiện tại
- [x] Tạo thư mục cho MCP server mới
- [x] Cài đặt MCP server filesystem
- [x] Cập nhật cấu hình cline_mcp_settings.json
- [ ] Kiểm tra và chứng minh khả năng của server
</task_progress>
</write_to_file>"""


# ===== FAKE RESPONSE GENERATOR =====

async def generate_fake_response():
    # Tạo request_id ngẫu nhiên
    request_id = f"fake-{uuid.uuid4().hex[:16]}"
    
    # Tạo fake response theo OpenAI SSE format
    fake_response = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [{
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": FAKE_CONTENT
            },
            "finish_reason": "stop",
            "logprobs": None
        }],
        "usage": {
            "prompt_tokens": 10000,
            "completion_tokens": len(FAKE_CONTENT.split()),
            "total_tokens": 1000 + len(FAKE_CONTENT.split())
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }
    
    # Yield SSE formatted chunks
    yield f"data: {json.dumps(fake_response)}\n\n".encode('utf-8')
    yield "data: [DONE]\n\n".encode('utf-8')