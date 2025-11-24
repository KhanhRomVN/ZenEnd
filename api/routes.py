import os
import re
import asyncio
import time
import uuid
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header, Response

def _extract_images_from_messages(messages: list) -> list[dict]:
    """
    Extract tất cả images từ messages.
    Trả về list các image objects với format: {type, data, format}
    """
    images = []
    
    for msg in messages:
        content = msg.content
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "image_url":
                        image_url_data = item.get("image_url", {})
                        
                        if isinstance(image_url_data, dict):
                            url = image_url_data.get("url", "")
                        elif isinstance(image_url_data, str):
                            url = image_url_data
                        else:
                            continue
                        
                        if url.startswith("data:image"):
                            import re
                            match = re.match(r'data:image/([a-zA-Z]+);base64,(.+)', url)
                            if match:
                                image_format = match.group(1)
                                base64_data = match.group(2)
                                
                                images.append({
                                    "type": "image_url",
                                    "format": image_format,
                                    "data": base64_data
                                })
    
    return images

def _extract_folder_path(messages: list) -> str | None:
    """
    Extract folder_path từ system/user messages.
    Tìm pattern: # Current Working Directory (/path/to/folder)
    """
    for msg in messages:
        content = msg.content
        if isinstance(content, str):
            match = re.search(
                r'# Current Working Directory \(([^)]+)\)',
                content
            )
            if match:
                folder_path = match.group(1)
                return folder_path
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    match = re.search(
                        r'# Current Working Directory \(([^)]+)\)',
                        text
                    )
                    if match:
                        folder_path = match.group(1)
                        return folder_path
    return None

def _detect_new_task(messages: list) -> bool:
    """
    Kiểm tra xem có <task></task> KHÔNG RỖNG trong MESSAGE CUỐI CÙNG không.
    Trả về True nếu đây là task mới (có nội dung task).
    """
    if not messages:
        return False
    
    latest_msg = messages[-1]
    content = latest_msg.content
    
    msg_role = latest_msg.role
    
    if isinstance(content, str):
        has_task_tag = '<task>' in content and '</task>' in content
        if has_task_tag:
            task_start_idx = content.find('<task>') + 6
            task_end_idx = content.find('</task>')
            task_content = content[task_start_idx:task_end_idx].strip()
            
            if len(task_content) == 0:
                return False
            
            return True
        else:
            return False
    elif isinstance(content, list):
        for idx, item in enumerate(content):
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                has_task_tag = '<task>' in text and '</task>' in text
                if has_task_tag:
                    task_start_idx = text.find('<task>') + 6
                    task_end_idx = text.find('</task>')
                    task_content = text[task_start_idx:task_end_idx].strip()
                    
                    if len(task_content) == 0:
                        return False
                    
                    return True
        return False
    else:
        return False

def _validate_and_fix_response(response: dict, request_id: str, is_fake: bool = False) -> dict:
    """
    Rebuild response từ ZenTab thành clean OpenAI completion format.
    Extract từng field và tạo lại object mới thay vì parse phức tạp.
    """
    if not isinstance(response, dict):
        return error_response(
            error_message="Invalid response format from ZenTab",
            detail_message="Response từ ZenTab không đúng format (không phải dict). Có thể ZenTab extension gặp lỗi.",
            metadata={"response_type": type(response).__name__},
            status_code=500,
            show_traceback=False
        )
    
    response_id = response.get('id', f'chatcmpl-{request_id}')
    object_type = response.get('object', 'chat.completion.chunk')
    created = response.get('created', int(time.time()))
    model = response.get('model', 'deepseek-chat')
    system_fingerprint = response.get('system_fingerprint', f'fp_{uuid.uuid4().hex[:8]}')
    
    original_choices = response.get('choices', [])
    if not original_choices or len(original_choices) == 0:
        return error_response(
            error_message="Invalid response: no choices",
            detail_message="Response từ ZenTab thiếu field 'choices'. Format response không hợp lệ.",
            metadata={"has_choices": bool(original_choices)},
            status_code=500,
            show_traceback=False
        )
    
    original_choice = original_choices[0]
    choice_index = original_choice.get('index', 0)
    finish_reason = original_choice.get('finish_reason', 'stop')
    logprobs = original_choice.get('logprobs', None)
    
    message_data = original_choice.get('message') or original_choice.get('delta', {})
    role = message_data.get('role', 'assistant')
    raw_content = message_data.get('content', '')
    tool_calls = message_data.get('tool_calls', None)
    
    content = raw_content
    if isinstance(raw_content, str) and '\\n' in raw_content:
        content = raw_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    
    original_usage = response.get('usage', {})
    prompt_tokens = original_usage.get('prompt_tokens', 0)
    completion_tokens = original_usage.get('completion_tokens', 0)
    total_tokens = original_usage.get('total_tokens', 0)
    
    if is_fake:
        message_obj = {
            'role': role,
            'content': content
        }
        if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
            message_obj['tool_calls'] = tool_calls
        
        choice_data = {
            'index': choice_index,
            'message': message_obj,
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }
    else:
        choice_data = {
            'index': choice_index,
            'delta': {
                'role': role,
                'content': content
            },
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }
    
    clean_response = {
        'id': response_id,
        'object': object_type,
        'created': created,
        'model': model,
        'choices': [choice_data],
        'usage': {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        },
        'system_fingerprint': system_fingerprint
    }
    
    return clean_response

from config.settings import REQUEST_TIMEOUT, HTTP_PORT
from models import ChatCompletionRequest
from .dependencies import verify_api_key
import uuid
import time
from core import error_response, is_fake_mode_enabled, generate_fake_response

router = APIRouter()

def setup_routes(app, port_manager):
    """Setup routes với port_manager dependency"""
    
    from fastapi.responses import JSONResponse
    
    @router.get("/v1/model/info")
    async def model_info(api_key: str = Depends(verify_api_key)):
        """
        Trả về thông tin model cho Cline extension
        """
        return {
            "id": "deepseek-chat",
            "object": "model",
            "created": 1234567890,
            "owned_by": "zenend",
            "permission": [],
            "root": "deepseek-chat",
            "parent": None,
            "description": "DeepSeek Chat via ZenTab extension"
        }

    @router.get("/v1/models")
    async def list_models(api_key: str = Depends(verify_api_key)):
        """
        Danh sách models (OpenAI compatible)
        """
        return {
            "object": "list",
            "data": [
                {
                    "id": "deepseek-chat",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "zenend"
                }
            ]
        }

    @router.get("/health")
    async def health_check():
        """
        Health check endpoint cho Render.com
        """
        return {
            "status": "healthy",
            "service": "ZenEnd Backend", 
            "version": "1.0.0",
            "timestamp": int(time.time()),
            "websocket_enabled": not os.getenv("RENDER")
        }
    
    @router.head("/health")
    async def health_check_head():
        """
        Handle HEAD requests từ Render health check
        """
        return Response(status_code=200)

    @router.post("/v1/chat/completions")
    async def chat_completions(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key)
    ):
        from fastapi.responses import StreamingResponse
        
        SUPPORTED_MODELS = ["deepseek-chat"]
        if request.model not in SUPPORTED_MODELS:
            return error_response(
                error_message=f"Unsupported model: {request.model}",
                detail_message=f"Model '{request.model}' không được hỗ trợ. Các model khả dụng: {', '.join(SUPPORTED_MODELS)}",
                metadata={"requested_model": request.model, "supported_models": SUPPORTED_MODELS},
                status_code=400,
                show_traceback=False
            )
        
        # 🆕 CHECK FAKE MODE - Trả về fake response ngay nếu enabled
        if is_fake_mode_enabled():
            from core import info
            from core.fake_response import FAKE_CONTENT
            
            request_id = f"fake-{uuid.uuid4().hex[:16]}"
            
            # Tạo full fake response với content
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
                    "prompt_tokens": 100,
                    "completion_tokens": len(FAKE_CONTENT.split()),
                    "total_tokens": 100 + len(FAKE_CONTENT.split())
                },
                "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
            }
            
            # Log fake response
            info(
                f"🎭 Sending FAKE response to client (Fake Mode Enabled)",
                {
                    "response_id": fake_response.get("id", "unknown"),
                    "request_id": request_id,
                    "fake_mode": True,
                    "object_type": fake_response.get("object", "unknown"),
                    "finish_reason": fake_response.get("choices", [{}])[0].get("finish_reason", "unknown") if fake_response.get("choices") else "unknown",
                    "content_length": len(FAKE_CONTENT)
                }
            )
            
            # Print toàn bộ fake response JSON (pretty format) với FULL content
            print(f"\n{'='*80}")
            print(f"[FAKE RESPONSE JSON - FULL]")
            print(f"{'='*80}")
            print(json.dumps(fake_response, indent=2, ensure_ascii=False))
            print(f"{'='*80}\n")
            
            return StreamingResponse(
                generate_fake_response(),
                media_type="text/event-stream"
            )
        
        max_connection_attempts = 3
        for attempt in range(max_connection_attempts):
            conn_status = port_manager.get_connection_status()
            
            if conn_status.get('websocket_connected') and conn_status.get('websocket_open'):
                break
            
            try:
                await port_manager.reconnect_websocket()
                await asyncio.sleep(1)
                
                conn_status = port_manager.get_connection_status()
                if conn_status.get('websocket_connected') and conn_status.get('websocket_open'):
                    break
                    
            except Exception as e:
                pass
            
            if attempt == max_connection_attempts - 1:
                return error_response(
                    error_message="WebSocket connection failed after retries",
                    detail_message="Không thể kết nối tới ZenTab extension. Vui lòng đảm bảo extension đang chạy và kết nối tới backend.",
                    metadata={"max_attempts": max_connection_attempts, "backend_port": HTTP_PORT},
                    status_code=503,
                    show_traceback=False
                )
            
            await asyncio.sleep(2)
        
        folder_path = _extract_folder_path(request.messages)
        is_new_task = _detect_new_task(request.messages)

        if is_new_task:
            available_tabs = await port_manager.request_fresh_tabs(timeout=10.0)
            
            if not available_tabs or len(available_tabs) == 0:
                return error_response(
                    error_message="No available tabs for new task",
                    detail_message="Không có tab DeepSeek nào khả dụng. Vui lòng mở ít nhất 1 tab DeepSeek trong ZenTab extension.",
                    metadata={"is_new_task": True, "available_tabs_count": 0},
                    status_code=503,
                    show_traceback=False
                )
            
            selected_tab = available_tabs[0]
        else:
            if not folder_path:
                return error_response(
                    error_message="Missing folder_path in request",
                    detail_message="Không tìm thấy folder_path trong request. Vui lòng đảm bảo task context được bao gồm trong messages.",
                    metadata={"is_new_task": False, "messages_count": len(request.messages)},
                    status_code=400,
                    show_traceback=False
                )
            
            folder_tabs = await port_manager.request_tabs_by_folder(folder_path, timeout=10.0)
            
            if not folder_tabs or len(folder_tabs) == 0:
                return error_response(
                    error_message=f"No tabs linked to folder: {folder_path}",
                    detail_message=f"Không có tab nào được liên kết với folder '{folder_path}'. Vui lòng bắt đầu một task mới trước.",
                    metadata={"folder_path": folder_path, "is_new_task": False},
                    status_code=503,
                    show_traceback=False
                )
            
            selected_tab = folder_tabs[0]
        
        tab_id = selected_tab.get('tabId')
        
        if not tab_id or not isinstance(tab_id, int) or tab_id <= 0:
            return error_response(
                error_message=f"Invalid tab ID from ZenTab: {tab_id}",
                detail_message=f"Nhận được tab ID không hợp lệ từ ZenTab extension: {tab_id}",
                metadata={"tab_id": tab_id, "tab_id_type": type(tab_id).__name__},
                status_code=500,
                show_traceback=False
            )
        
        # 🆕 EXTRACT IMAGES từ messages
        images = _extract_images_from_messages(request.messages)
        has_images = len(images) > 0
        
        if has_images:
            from core import info
            info(
                f"📸 Extracted {len(images)} image(s) from request",
                {
                    "request_id": request_id,
                    "tab_id": tab_id,
                    "image_count": len(images),
                    "image_formats": [img["format"] for img in images]
                }
            )
        
        tab_status = selected_tab.get('status', 'unknown')
        can_accept = selected_tab.get('canAccept', False)
        
        if tab_status != 'free' or not can_accept:
            return error_response(
                error_message=f"Tab not ready: status={tab_status}, can_accept={can_accept}",
                detail_message=f"Tab không sẵn sàng nhận request. Trạng thái: {tab_status}, Có thể nhận: {can_accept}",
                metadata={"tab_id": tab_id, "tab_status": tab_status, "can_accept": can_accept},
                status_code=503,
                show_traceback=False
            )

        request_id = f"api-{uuid.uuid4().hex[:16]}"

        system_messages = [msg for msg in request.messages if msg.role == "system"]
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        
        if not user_messages:
            return error_response(
                error_message="No user message in request",
                detail_message="Không tìm thấy user message trong request. Request phải chứa ít nhất một message có role='user'.",
                metadata={"total_messages": len(request.messages), "system_messages": len(system_messages)},
                status_code=400,
                show_traceback=False
            )

        system_prompt = ""
        if is_new_task and system_messages:
            system_content = system_messages[0].content
            if isinstance(system_content, str):
                system_prompt = system_content
            elif isinstance(system_content, list):
                text_parts = []
                for item in system_content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                system_prompt = "\n\n".join(text_parts)
        
        raw_content = user_messages[-1].content
        
        if isinstance(raw_content, list):
            text_parts = []
            for item in raw_content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        text_parts.append("[IMAGE - Not supported]")
            
            user_prompt = "\n\n".join(text_parts)
        else:
            user_prompt = raw_content

        port_manager.request_to_tab[request_id] = tab_id
        
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "systemPrompt": system_prompt,
            "userPrompt": user_prompt,
            "requestId": request_id,
            "isNewTask": is_new_task
        }
        
        if is_new_task and folder_path:
            ws_message["folderPath"] = folder_path
        
        # 🆕 Thêm images vào message nếu có
        if has_images:
            ws_message["images"] = images
        
        try:
            await port_manager.websocket.send(json.dumps(ws_message))
        except Exception as e:
            port_manager.request_to_tab.pop(request_id, None)
            return error_response(
                error_message=f"Failed to send prompt to tab {tab_id}",
                detail_message=f"Không thể gửi prompt tới tab. Lỗi: {str(e)}",
                metadata={"tab_id": tab_id, "request_id": request_id, "error_type": type(e).__name__},
                status_code=500,
                show_traceback=True
            )
        
        try:
            response = await port_manager.wait_for_response(request_id, REQUEST_TIMEOUT)
            
            if "error" in response:
                error_msg = response["error"]
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    return error_response(
                        error_message=f"Tab cooling down or not ready",
                        detail_message=error_msg,
                        metadata={"tab_id": tab_id, "request_id": request_id, "error_type": "cooling_down"},
                        status_code=503,
                        show_traceback=False
                    )
                else:
                    return error_response(
                        error_message=f"Error from tab response",
                        detail_message=error_msg,
                        metadata={"tab_id": tab_id, "request_id": request_id},
                        status_code=500,
                        show_traceback=False
                    )
            
            port_manager.mark_request_completed(request_id)

            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=30.0))
            
            response = _validate_and_fix_response(response, request_id, is_fake=False)
            
            # 🆕 Log response thành công trước khi gửi về Cline
            from core import info
            info(
                f"✅ Sending successful response to client",
                {
                    "response_id": response.get("id", "unknown"),
                    "request_id": request_id,
                    "tab_id": tab_id,
                    "object_type": response.get("object", "unknown"),
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason", "unknown") if response.get("choices") else "unknown",
                    "content_length": len(response.get("choices", [{}])[0].get("message", {}).get("content", "")) if response.get("choices") else 0
                }
            )
            
            # 🆕 Print toàn bộ response JSON (pretty format) để debug
            print(f"\n{'='*80}")
            print(f"[SUCCESS RESPONSE JSON]")
            print(f"{'='*80}")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print(f"{'='*80}\n")
            
            if response.get("object") == "chat.completion.chunk":
                async def generate_real():
                    yield f"data: {json.dumps(response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    generate_real(),
                    media_type="text/event-stream"
                )
            else:
                return response
            
        except HTTPException as he:
            port_manager.mark_request_processed(request_id)
            
            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=10.0))
            
            if he.status_code == 503:
                return error_response(
                    error_message="Service unavailable",
                    detail_message=he.detail if hasattr(he, 'detail') else "Dịch vụ tạm thời không khả dụng. Vui lòng thử lại sau.",
                    metadata={"tab_id": tab_id, "request_id": request_id, "status_code": 503},
                    status_code=503,
                    show_traceback=False
                )

            else:
                fallback_response = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "deepseek-chat",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I apologize, but I'm experiencing temporary technical difficulties. Please try your request again in a moment."
                        },
                        "finish_reason": "stop",
                        "logprobs": None
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    },
                    "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
                }
                
                return fallback_response
        except Exception as e:
            port_manager.mark_request_processed(request_id)
            
            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=10.0))
            
            return error_response(
                error_message=f"Unexpected error processing request",
                detail_message=f"Đã xảy ra lỗi không mong muốn: {str(e)}",
                metadata={"request_id": request_id, "error_type": type(e).__name__},
                status_code=500,
                show_traceback=True
            )
            
        finally:
            pass
    
    app.include_router(router)