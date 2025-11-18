"""
Fake response generator cho testing - Cline XML Format
"""
import uuid
import time
import re
from typing import List, Any, Optional, Dict, Tuple

def _is_plan_mode(messages: List[Any]) -> bool:
    """Kiểm tra xem Cline có đang ở PLAN MODE không"""
    if not messages:
        return False
        
    for msg in messages:
        if hasattr(msg, 'content'):
            content = msg.content
        elif hasattr(msg, 'get'):
            content = msg.get('content', '')
        else:
            continue
            
        # Kiểm tra trong environment_details
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text = item.get('text', '')
                    if 'Current Mode\nPLAN MODE' in text:
                        return True
        elif isinstance(content, str) and 'Current Mode\nPLAN MODE' in content:
            return True
            
    return False

def create_fake_response(model: str = "deepseek-chat", messages: List[Any] = None, stream: bool = False) -> dict:
    """
    Tạo fake response chuẩn OpenAI để test backend mà không cần gọi DeepSeek thực sự.
    Hỗ trợ cả streaming và non-streaming responses.
    """
    # Kiểm tra xem có đang ở PLAN MODE không
    is_plan_mode = _is_plan_mode(messages)
    
    if is_plan_mode:
        return _create_plan_mode_response(model, messages, stream)
    
    # ƯU TIÊN: Kiểm tra <task> tag trước
    if messages and _contains_task_tag(messages):
        task_content = _extract_task_content(messages)
        # Sử dụng response chuẩn cho các task đơn giản
        if any(simple_task in task_content.lower() for simple_task in ['hello', 'hi', 'xin chào', 'test']):
            return _create_attempt_completion_response(model, task_content, stream)
        else:
            return _create_task_response_with_xml(model, messages, stream)
    # Kiểm tra nếu có messages và có chứa tool use pattern
    elif messages and _contains_tool_use_pattern(messages):
        return _create_xml_tool_call_response(model, stream)
    else:
        return _create_standard_response(model, stream)


def _contains_task_tag(messages: List[Any]) -> bool:
    """Kiểm tra nếu messages có chứa <task> tag trong user message"""
    for msg in messages:
        # Xử lý cả object và dict
        if hasattr(msg, 'role'):
            role = msg.role
            content = msg.content
        elif hasattr(msg, 'get'):
            role = msg.get('role')
            content = msg.get('content', '')
        else:
            continue

        if role != "user":
            continue

        # Xử lý content dạng list (multimodal)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    if '<task>' in item.get('text', '').lower():
                        return True
        elif isinstance(content, str) and '<task>' in content.lower():
            return True
    
    return False


def _contains_tool_use_pattern(messages: List[Any]) -> bool:
    """Kiểm tra nếu messages có chứa pattern sử dụng tool"""
    for msg in messages:
        # Xử lý cả object và dict
        if hasattr(msg, 'role'):
            role = msg.role
            content = msg.content
        elif hasattr(msg, 'get'):
            role = msg.get('role')
            content = msg.get('content', '')
        else:
            continue
        
        # Kiểm tra nếu có system message với TOOL USE
        if role == "system" and "TOOL USE" in str(content):
            return True
    
    return False


def _create_task_response_with_xml(model: str, messages: List[Any], stream: bool = False) -> dict:
    """
    Tạo response với XML khi nhận được <task> từ user (Cline cần XML)
    Hỗ trợ cả streaming và non-streaming
    """
    task_content = _extract_task_content(messages)
    
    # Tạo XML content dựa trên nội dung task
    if "hello" in task_content.lower():
        xml_content = """<thinking>
User sent a greeting "hello". I'll respond with attempt_completion and create a simple task progress.
</thinking>

<attempt_completion>
<result>Hello! I've received your greeting and I'm ready to assist you with the ZenEnd project. Please let me know your specific requirements.</result>
<task_progress>
- [x] Acknowledge user greeting
- [ ] Wait for specific task requirements
</task_progress>
</attempt_completion>"""
    elif "test" in task_content.lower():
        xml_content = """<thinking>
The user is testing the API. I should examine the project structure to understand how it works.
</thinking>

<read_file>
<path>main.py</path>
<task_progress>
- [ ] Analyze main application structure
- [ ] Review API routes implementation  
- [ ] Test API functionality
- [ ] Verify response format
</task_progress>
</read_file>"""
    elif "api" in task_content.lower() or "route" in task_content.lower():
        xml_content = """<thinking>
The user wants to understand API routes. I should examine the API implementation.
</thinking>

<read_file>
<path>api/routes.py</path>
<task_progress>
- [ ] Analyze API routes structure
- [ ] Review request handling
- [ ] Check response formatting
- [ ] Test endpoint functionality
</task_progress>
</read_file>"""
    elif "websocket" in task_content.lower() or "socket" in task_content.lower():
        xml_content = """<thinking>
The user is interested in WebSocket functionality. I should examine the WebSocket implementation.
</thinking>

<read_file>
<path>websocket/server.py</path>
<task_progress>
- [ ] Analyze WebSocket server
- [ ] Review connection handling
- [ ] Check message processing
- [ ] Test real-time functionality
</task_progress>
</read_file>"""
    elif "fake" in task_content.lower():
        xml_content = """<thinking>
The user wants to understand the fake response system. I should examine the current implementation.
</thinking>

<read_file>
<path>api/fake_response.py</path>
<task_progress>
- [ ] Analyze fake response system
- [ ] Review response generation
- [ ] Check test scenarios
- [ ] Improve fake response logic
</task_progress>
</read_file>"""
    else:
        xml_content = f"""<thinking>
The user wants me to work on: {task_content}. I need to understand the project structure first.
</thinking>

<list_files>
<path>.</path>
<recursive>true</recursive>
<task_progress>
- [ ] Analyze task requirements: {task_content}
- [ ] Explore project structure
- [ ] Identify relevant files and components
- [ ] Develop implementation strategy
</task_progress>
</list_files>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": _calculate_tokens(messages),
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": _calculate_tokens(messages) + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def _create_attempt_completion_response(model: str, task_content: str, stream: bool = False) -> dict:
    """
    Tạo response với attempt_completion cho Cline (cần XML format)
    Hỗ trợ cả streaming và non-streaming
    """
    xml_content = f"""<thinking>
Người dùng đã gửi task: "{task_content}". Vì đây là một task đơn giản không đòi hỏi code cụ thể, tôi sẽ dùng attempt_completion để phản hồi và đồng thời tạo một task_progress list đơn giản cho các bước tiếp theo.
</thinking>

<attempt_completion>
<result>I've received your task: "{task_content}". I'm currently in fake response mode and ready to assist you with the ZenEnd project. Please provide more specific requirements.</result>
<task_progress>
- [x] Receive and acknowledge user task
- [ ] Wait for specific requirements
</task_progress>
</attempt_completion>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": _calculate_tokens([]),
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": _calculate_tokens([]) + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def _extract_task_content(messages: List[Any]) -> str:
    """Trích xuất nội dung từ <task> tag"""
    for msg in messages:
        # Xử lý cả object và dict
        if hasattr(msg, 'role'):
            role = msg.role
            content = msg.content
        elif hasattr(msg, 'get'):
            role = msg.get('role')
            content = msg.get('content', '')
        else:
            continue

        if role != "user":
            continue

        # Xử lý content dạng list (multimodal)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text_content = item.get('text', '')
                    task_content = _extract_task_from_text(text_content)
                    if task_content:
                        return task_content
        elif isinstance(content, str):
            task_content = _extract_task_from_text(content)
            if task_content:
                return task_content
    
    return "Unknown task"


def _extract_task_from_text(text: str) -> str:
    """Trích xuất nội dung task từ text"""
    # Tìm nội dung giữa <task> tags
    task_match = re.search(r'<task>(.*?)</task>', text, re.IGNORECASE | re.DOTALL)
    if task_match:
        return task_match.group(1).strip()
    
    # Nếu không có tag, tìm dòng chứa "task" hoặc nội dung đơn giản
    lines = text.split('\n')
    for line in lines:
        if line.strip() and not line.strip().startswith('#') and 'task' not in line.lower():
            return line.strip()
    
    return ""


def _create_xml_tool_call_response(model: str, stream: bool = False) -> dict:
    """
    Tạo response với XML tool calls cho Cline (Cline cần XML trong content)
    Hỗ trợ cả streaming và non-streaming
    """
    xml_content = """<thinking>
I need to examine the current files to understand the task and create a plan. Let me start by reading the main application file to see the project structure.
</thinking>

<read_file>
<path>main.py</path>
<task_progress>
- [ ] Analyze project structure and main entry point
- [ ] Examine API routes and request handling
- [ ] Review response parsing logic
- [ ] Understand provider LLM interaction flow
</task_progress>
</read_file>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def _create_standard_response(model: str, stream: bool = False) -> dict:
    """
    Tạo response tiêu chuẩn cho Cline (cần XML format)
    Hỗ trợ cả streaming và non-streaming
    """
    xml_content = """<thinking>
The user is interacting with the ZenEnd backend project. I should provide a helpful response and offer to explore the project structure.
</thinking>

<attempt_completion>
<result>Hello! I can see you're working with the ZenEnd backend project. I notice this is a FastAPI application with WebSocket support for bridging with ZenTab extension. The project structure includes API routes, WebSocket handlers, and core management components. How can I help you with this project?</result>
<task_progress>
- [x] Initialize conversation with user
- [ ] Wait for user's specific requirements
</task_progress>
</attempt_completion>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def _create_streaming_response(model: str, content: str) -> dict:
    """
    Tạo streaming response đơn giản - chỉ 1 chunk với toàn bộ content
    Đây là format mà Cline thực sự mong đợi
    """
    response_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
    created_time = int(time.time())
    
    # Chunk duy nhất với toàn bộ content
    chunk = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": created_time,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": content
            },
            "finish_reason": "stop",
            "logprobs": None
        }],
        "usage": {
            "prompt_tokens": 285,
            "completion_tokens": _count_tokens(content),
            "total_tokens": 285 + _count_tokens(content)
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }
    
    return chunk

def create_fake_response_with_multiple_tools(model: str = "deepseek-chat", stream: bool = False) -> dict:
    """
    Tạo fake response với multiple tool calls
    """
    xml_content = """I'll help you explore the ZenEnd backend project. Let me start by examining the main application structure and API routes.

<read_file>
<path>main.py</path>
</read_file>

<read_file>
<path>api/routes.py</path>
</read_file>

<task_progress>
- [ ] Analyze main application structure
- [ ] Review API routes implementation
- [ ] Understand WebSocket handlers
- [ ] Test backend functionality
</task_progress>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_response_with_execute_command(model: str = "deepseek-chat", stream: bool = False) -> dict:
    """
    Tạo fake response với execute command
    """
    xml_content = """Let me check if the backend server is running and test the API.

<execute_command>
<command>python main.py</command>
<requires_approval>false</requires_approval>
</execute_command>

<task_progress>
- [ ] Start backend server
- [ ] Test API endpoints
- [ ] Verify WebSocket connection
- [ ] Validate response format
</task_progress>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_response_with_list_files(model: str = "deepseek-chat", stream: bool = False) -> dict:
    """
    Tạo fake response với list files
    """
    xml_content = """Let me first explore the project structure to understand the codebase better.

<list_files>
<path>.</path>
<recursive>true</recursive>
</list_files>

<task_progress>
- [ ] Explore project structure
- [ ] Identify key components
- [ ] Analyze code organization
- [ ] Understand dependencies
</task_progress>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_response_with_read_file(model: str = "deepseek-chat", file_path: str = "main.py", stream: bool = False) -> dict:
    """
    Tạo fake response với read file
    """
    xml_content = f"""Let me examine the {file_path} file to understand the implementation and how it handles API requests.

<read_file>
<path>{file_path}</path>
<task_progress>
- [ ] Analyze {file_path} structure and components
- [ ] Understand request processing flow
- [ ] Identify key functions and classes for API handling
- [ ] Review response generation logic
- [ ] Document integration with provider LLM
</task_progress>
</read_file>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_error_response(model: str = "deepseek-chat", error_msg: str = "Test error", stream: bool = False) -> dict:
    """
    Tạo fake error response cho testing
    """
    if stream:
        return _create_streaming_response(model, f"Error: {error_msg}")
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Error: {error_msg}",
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": 15,
                "total_tokens": 300
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_task_response(model: str = "deepseek-chat", task_description: str = "", stream: bool = False) -> dict:
    """
    Tạo fake response cụ thể cho task
    """
    if not task_description:
        task_description = "the requested task"
    
    xml_content = f"""I understand you want me to work on: {task_description}

Let me start by exploring the project structure to understand the current implementation.

<list_files>
<path>.</path>
<recursive>true</recursive>
<task_progress>
- [ ] Analyze task requirements: {task_description}
- [ ] Explore project structure
- [ ] Identify relevant files and components
- [ ] Develop implementation strategy
</task_progress>
</list_files>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }


def create_fake_response_with_specific_task(model: str = "deepseek-chat", task_type: str = "explore", stream: bool = False) -> dict:
    """
    Tạo fake response cho loại task cụ thể
    """
    task_responses = {
        "explore": create_fake_response_with_list_files,
        "api": lambda m, s: create_fake_response_with_read_file(m, "api/routes.py", s),
        "websocket": lambda m, s: create_fake_response_with_read_file(m, "websocket/server.py", s),
        "fake": lambda m, s: create_fake_response_with_read_file(m, "api/fake_response.py", s),
        "main": lambda m, s: create_fake_response_with_read_file(m, "main.py", s)
    }
    
    return task_responses.get(task_type, lambda m, s: create_fake_task_response(m, "", s))(model, stream)


def _calculate_tokens(messages: List[Any]) -> int:
    """Tính toán số tokens từ messages (ước lượng)"""
    if not messages:
        return 285
    
    total_tokens = 0
    for msg in messages:
        # Xử lý cả object và dict
        if hasattr(msg, 'content'):
            content = msg.content
        elif hasattr(msg, 'get'):
            content = msg.get('content', '')
        else:
            continue
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    total_tokens += _count_tokens(item.get('text', ''))
        elif isinstance(content, str):
            total_tokens += _count_tokens(content)
    
    return max(total_tokens, 285)  # Minimum token count

def _count_tokens(text: str) -> int:
    """Đếm số tokens trong text (ước lượng)"""
    # Ước lượng đơn giản: 1 token ~ 4 characters
    return max(len(text) // 4, 1)


def is_fake_mode_enabled() -> bool:
    """
    Kiểm tra có bật fake mode không
    """
    return True  # Hiện tại đang bật fake mode


# Các hàm tiện ích để tạo response cụ thể
def get_response_for_testing(stream: bool = False) -> dict:
    """Trả về response mẫu cho testing Cline integration"""
    return create_fake_response_with_list_files("deepseek-chat", stream)


def get_response_for_specific_tool(tool_name: str, stream: bool = False) -> dict:
    """Trả về response với tool cụ thể"""
    tool_responses = {
        "read_file": create_fake_response_with_multiple_tools,
        "execute_command": create_fake_response_with_execute_command,
        "list_files": create_fake_response_with_list_files,
        "task": create_fake_task_response
    }
    
    return tool_responses.get(tool_name, create_fake_response)(stream=stream)


def get_response_for_task(task_description: str = "", stream: bool = False) -> dict:
    """Trả về response cho task cụ thể"""
    return create_fake_task_response("deepseek-chat", task_description, stream)


def get_response_for_task_type(task_type: str = "explore", stream: bool = False) -> dict:
    """Trả về response cho loại task cụ thể"""
    return create_fake_response_with_specific_task("deepseek-chat", task_type, stream)


# Response templates for common scenarios
RESPONSE_TEMPLATES = {
    "simple_task": {
        "content": """<thinking>
User sent a simple task. I'll respond with attempt_completion.
</thinking>

<attempt_completion>
<result>I've received your task. I'm currently in fake response mode and ready to assist you with the ZenEnd project.</result>
<task_progress>
- [x] Acknowledge user task
- [ ] Wait for specific requirements
</task_progress>
</attempt_completion>""",
        "usage": {"prompt_tokens": 285, "completion_tokens": 85, "total_tokens": 370}
    },
    "project_exploration": {
        "content": """I'll help you explore the ZenEnd backend project. Let me start by examining the project structure.

<list_files>
<path>.</path>
<recursive>true</recursive>
<task_progress>
- [ ] Explore project structure
- [ ] Identify key components
- [ ] Analyze code organization
- [ ] Understand dependencies
</task_progress>
</list_files>""",
        "usage": {"prompt_tokens": 285, "completion_tokens": 72, "total_tokens": 357}
    },
    "api_analysis": {
        "content": """I'll analyze the API routes implementation.

<read_file>
<path>api/routes.py</path>
<task_progress>
- [ ] Analyze API routes structure
- [ ] Review request handling
- [ ] Check response formatting
- [ ] Test endpoint functionality
</task_progress>
</read_file>""",
        "usage": {"prompt_tokens": 285, "completion_tokens": 68, "total_tokens": 353}
    },
    "websocket_analysis": {
        "content": """I'll examine the WebSocket implementation.

<read_file>
<path>websocket/server.py</path>
<task_progress>
- [ ] Analyze WebSocket server
- [ ] Review connection handling
- [ ] Check message processing
- [ ] Test real-time functionality
</task_progress>
</read_file>""",
        "usage": {"prompt_tokens": 285, "completion_tokens": 70, "total_tokens": 355}
    }
}

def create_fake_attempt_completion_response(model: str = "deepseek-chat", result: str = "", task_progress: str = "", stream: bool = False) -> dict:
    if not result:
        result = "I've completed your task. I'm currently in fake response mode and ready to assist you with the ZenEnd project."
    
    if not task_progress:
        task_progress = """- [x] Receive and acknowledge user task
- [x] Process task
- [ ] Wait for next specific requirements"""

    xml_content = f"""<thinking>
I'm completing the user's task with the provided result and task progress.
</thinking>

<attempt_completion>
<result>{result}</result>
<task_progress>
{task_progress}
</task_progress>
</attempt_completion>"""

    if stream:
        return _create_streaming_response(model, xml_content)
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": xml_content,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 285,
                "completion_tokens": _count_tokens(xml_content),
                "total_tokens": 285 + _count_tokens(xml_content)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def create_response_from_template(template_name: str, model: str = "deepseek-chat", stream: bool = False) -> dict:
    """Tạo response từ template"""
    template = RESPONSE_TEMPLATES.get(template_name, RESPONSE_TEMPLATES["project_exploration"])
    
    if stream:
        return _create_streaming_response(model, template["content"])
    else:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": template["content"],
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": template["usage"],
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }

def _create_plan_mode_response(model: str, messages: List[Any], stream: bool = False) -> dict:
    """
    Tạo response cho PLAN MODE - không dùng XML tool calls
    """
    plan_response = """I can see you're in PLAN MODE and you've sent a simple "hello" task. Since this is a straightforward greeting, I don't need extensive planning. I'm ready to help you with the ZenEnd backend project. 

The project structure looks well-organized with API routes, WebSocket handlers, and core management components. I can assist with exploring the codebase, implementing features, or debugging issues.

Would you like me to switch to ACT MODE to start working on specific tasks, or do you have a particular planning discussion in mind?"""

    if stream:
        # Streaming response cho PLAN MODE
        return _create_streaming_response(model, plan_response)
    else:
        # Non-streaming response cho PLAN MODE  
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": plan_response,
                    "tool_calls": None
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": _calculate_tokens(messages) if messages else 285,
                "completion_tokens": _count_tokens(plan_response),
                "total_tokens": (_calculate_tokens(messages) if messages else 285) + _count_tokens(plan_response)
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }