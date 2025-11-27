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
    🔥 CRITICAL: Wrapped trong try-catch để không crash nếu có lỗi
    """
    images = []
    
    try:
        if not messages or not isinstance(messages, list):
            return images
        
        for msg_idx, msg in enumerate(messages):
            try:
                # Validate msg structure
                if not hasattr(msg, 'content'):
                    continue
                
                content = msg.content
                
                if isinstance(content, list):
                    for item_idx, item in enumerate(content):
                        try:
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
                                            
                                            # Validate base64 data (basic check)
                                            if base64_data and len(base64_data) > 0:
                                                images.append({
                                                    "type": "image_url",
                                                    "format": image_format,
                                                    "data": base64_data
                                                })
                        except Exception as item_error:
                            # Log item error nhưng không crash
                            from core import warning
                            warning(
                                f"Failed to process image item {item_idx} in message {msg_idx}",
                                {"error": str(item_error), "error_type": type(item_error).__name__}
                            )
                            continue
                            
            except Exception as msg_error:
                # Log message error nhưng không crash
                from core import warning
                warning(
                    f"Failed to process message {msg_idx}",
                    {"error": str(msg_error), "error_type": type(msg_error).__name__}
                )
                continue
        
    except Exception as e:
        # Log top-level error nhưng trả về empty list thay vì crash
        from core import error
        error(
            f"Critical error in _extract_images_from_messages",
            {"error": str(e), "error_type": type(e).__name__},
            show_traceback=True
        )
        return []
    
    return images

def _extract_folder_path(messages: list) -> str | None:
    """
    Extract folder_path từ system/user messages.
    Tìm pattern: # Current Working Directory (/path/to/folder)
    🔥 CRITICAL: Wrapped trong try-catch để không crash
    """
    try:
        if not messages or not isinstance(messages, list):
            return None
        
        for msg in messages:
            try:
                if not hasattr(msg, 'content'):
                    continue
                
                content = msg.content
                
                if isinstance(content, str):
                    match = re.search(
                        r'# Current Working Directory \(([^)]+)\)',
                        content
                    )
                    if match:
                        folder_path = match.group(1)
                        # Validate folder_path is not empty
                        if folder_path and folder_path.strip():
                            return folder_path.strip()
                            
                elif isinstance(content, list):
                    for item in content:
                        try:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text = item.get("text", "")
                                if text:
                                    match = re.search(
                                        r'# Current Working Directory \(([^)]+)\)',
                                        text
                                    )
                                    if match:
                                        folder_path = match.group(1)
                                        if folder_path and folder_path.strip():
                                            return folder_path.strip()
                        except Exception:
                            continue
                            
            except Exception:
                continue
                
    except Exception as e:
        from core import warning
        warning(
            f"Error in _extract_folder_path",
            {"error": str(e), "error_type": type(e).__name__}
        )
        return None
    
    return None

def _detect_new_task(messages: list) -> bool:
    """
    Kiểm tra xem có <task></task> KHÔNG RỖNG trong MESSAGE CUỐI CÙNG không.
    Trả về True nếu đây là task mới (có nội dung task).
    🔥 CRITICAL: Wrapped trong try-catch, default False nếu có lỗi
    """
    try:
        if not messages or not isinstance(messages, list) or len(messages) == 0:
            return False
        
        latest_msg = messages[-1]
        
        if not hasattr(latest_msg, 'content'):
            return False
        
        content = latest_msg.content
        
        if isinstance(content, str):
            has_task_tag = '<task>' in content and '</task>' in content
            if has_task_tag:
                try:
                    task_start_idx = content.find('<task>') + 6
                    task_end_idx = content.find('</task>')
                    
                    # Validate indices
                    if task_end_idx <= task_start_idx:
                        return False
                    
                    task_content = content[task_start_idx:task_end_idx].strip()
                    
                    if len(task_content) == 0:
                        return False
                    
                    return True
                except Exception:
                    return False
            else:
                return False
                
        elif isinstance(content, list):
            for idx, item in enumerate(content):
                try:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        if not text:
                            continue
                        
                        has_task_tag = '<task>' in text and '</task>' in text
                        if has_task_tag:
                            task_start_idx = text.find('<task>') + 6
                            task_end_idx = text.find('</task>')
                            
                            # Validate indices
                            if task_end_idx <= task_start_idx:
                                continue
                            
                            task_content = text[task_start_idx:task_end_idx].strip()
                            
                            if len(task_content) == 0:
                                continue
                            
                            return True
                except Exception:
                    continue
                    
            return False
        else:
            return False
            
    except Exception as e:
        from core import warning
        warning(
            f"Error in _detect_new_task",
            {"error": str(e), "error_type": type(e).__name__}
        )
        return False

def _validate_and_fix_response(response: dict, request_id: str, is_fake: bool = False) -> dict:
    """
    Rebuild response từ ZenTab thành clean OpenAI completion format.
    Extract từng field và tạo lại object mới thay vì parse phức tạp.
    🔥 CRITICAL: Bọc toàn bộ logic trong try-catch để tránh crash
    """
    try:
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
        
        # 🔥 CRITICAL: Validate original_choice là dict
        if not isinstance(original_choice, dict):
            return error_response(
                error_message="Invalid choice format",
                detail_message=f"Choice[0] không đúng format (type: {type(original_choice).__name__}). Expected dict.",
                metadata={"choice_type": type(original_choice).__name__},
                status_code=500,
                show_traceback=False
            )
        
        choice_index = original_choice.get('index', 0)
        finish_reason = original_choice.get('finish_reason', 'stop')
        logprobs = original_choice.get('logprobs', None)
        
        message_data = original_choice.get('message') or original_choice.get('delta', {})
        
        # 🔥 CRITICAL: Validate message_data là dict
        if not isinstance(message_data, dict):
            message_data = {}
        
        role = message_data.get('role', 'assistant')
        raw_content = message_data.get('content', '')
        tool_calls = message_data.get('tool_calls', None)
        
        # 🔥 CRITICAL: Ensure content is always string
        if raw_content is None:
            content = ""
        elif isinstance(raw_content, str):
            if '\\n' in raw_content:
                content = raw_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
            else:
                content = raw_content
        else:
            content = str(raw_content)
        
        original_usage = response.get('usage', {})
        
        # 🔥 CRITICAL: Validate usage is dict
        if not isinstance(original_usage, dict):
            original_usage = {}
        
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
    
    except Exception as e:
        # 🔥 CRITICAL: Catch mọi exception trong quá trình rebuild
        import traceback
        traceback.print_exc()
        
        return error_response(
            error_message=f"Exception while validating response: {str(e)}",
            detail_message=f"Lỗi không mong muốn khi xử lý response từ ZenTab: {str(e)}. Response có thể bị corrupt hoặc format không hợp lệ.",
            metadata={
                "exception_type": type(e).__name__,
                "request_id": request_id,
                "response_preview": str(response)[:200] if response else "None"
            },
            status_code=500,
            show_traceback=True
        )

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
            
            return StreamingResponse(
                generate_fake_response(),
                media_type="text/event-stream"
            )
        
        conn_status = port_manager.get_connection_status()
        
        if not (conn_status.get('websocket_connected') and conn_status.get('websocket_open')):
            return error_response(
                error_message="WebSocket not connected",
                detail_message="ZenTab extension chưa kết nối tới backend. Vui lòng đảm bảo extension đang chạy và đã connect tới WebSocket.",
                metadata={
                    "websocket_connected": conn_status.get('websocket_connected'),
                    "websocket_open": conn_status.get('websocket_open'),
                    "backend_port": HTTP_PORT
                },
                status_code=503,
                show_traceback=False
            )
                
        folder_path = _extract_folder_path(request.messages)
        is_new_task = _detect_new_task(request.messages)

        if is_new_task:
            available_tabs = await port_manager.request_fresh_tabs(timeout=10.0)
            
            if not available_tabs or len(available_tabs) == 0:
                return error_response(
                    error_message="No available tabs for new task",
                    detail_message="Không có tab DeepSeek nào khả dụng hoặc tất cả tabs đang busy. Vui lòng đợi hoặc mở thêm tab DeepSeek.",
                    metadata={"is_new_task": True, "available_tabs_count": 0},
                    status_code=503,
                    show_traceback=False
                )
            
            # 🔥 NEW: Ưu tiên tab KHÔNG có folder_path hoặc có folder_path TRÙNG
            if folder_path:
                matching_tabs = [t for t in available_tabs if t.get('folderPath') == folder_path or t.get('folderPath') is None]
                if matching_tabs:
                    selected_tab = matching_tabs[0]
                else:
                    selected_tab = available_tabs[0]
                    from core import warning
                    warning(
                        f"No matching tabs for folder '{folder_path}', using first available tab",
                        {"folder_path": folder_path, "selected_tab_id": selected_tab.get('tabId')}
                    )
            else:
                no_folder_tabs = [t for t in available_tabs if t.get('folderPath') is None]
                selected_tab = no_folder_tabs[0] if no_folder_tabs else available_tabs[0]
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
                    detail_message=f"Không có tab nào rảnh được liên kết với folder '{folder_path}'. Các tab có thể đang busy hoặc chưa được link.",
                    metadata={"folder_path": folder_path, "is_new_task": False},
                    status_code=503,
                    show_traceback=False
                )
            
            # 🔥 FIX: Double-check canAccept để chắc chắn tab thực sự rảnh
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
        
        # 🆕 EXTRACT IMAGES từ messages với error handling
        try:
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
        except Exception as e:
            # 🔥 CRITICAL: Nếu extract images fail, vẫn tiếp tục (images = [])
            from core import warning
            warning(
                f"Failed to extract images from messages: {str(e)}",
                {"request_id": request_id, "error_type": type(e).__name__}
            )
            images = []
            has_images = False
        
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
        
        # 🆕 LOG: Chi tiết về isNewTask decision
        from core import info
        info(
            f"📤 Preparing to send prompt to tab {tab_id}",
            {
                "request_id": request_id,
                "tab_id": tab_id,
                "is_new_task": is_new_task,
                "folder_path": folder_path or "None",
                "tab_folder_path": selected_tab.get('folderPath') or "None",
                "has_system_prompt": bool(system_prompt and system_prompt.strip()),
                "user_prompt_length": len(user_prompt),
                "system_prompt_length": len(system_prompt) if system_prompt else 0
            }
        )

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
        
        # 🔥 CRITICAL FIX: Gửi folderPath cho MỌI request (không chỉ new task)
        # Extension CẦN folderPath để accumulate tokens
        if folder_path:
            ws_message["folderPath"] = folder_path
        
        # 🆕 Thêm images vào message nếu có
        if has_images:
            ws_message["images"] = images
        
        try:
            # 🔥 CRITICAL: Validate WebSocket state trước khi gửi
            if not port_manager.websocket:
                return error_response(
                    error_message="WebSocket connection lost",
                    detail_message="WebSocket đã bị disconnect trước khi gửi prompt. Vui lòng reconnect ZenTab extension.",
                    metadata={"tab_id": tab_id, "request_id": request_id},
                    status_code=503,
                    show_traceback=False
                )
            
            # Check WebSocket state (FastAPI WebSocket)
            if hasattr(port_manager.websocket, 'client_state'):
                from starlette.websockets import WebSocketState
                if port_manager.websocket.client_state != WebSocketState.CONNECTED:
                    return error_response(
                        error_message="WebSocket not in CONNECTED state",
                        detail_message=f"WebSocket state: {port_manager.websocket.client_state}. Không thể gửi message.",
                        metadata={"tab_id": tab_id, "request_id": request_id, "ws_state": str(port_manager.websocket.client_state)},
                        status_code=503,
                        show_traceback=False
                    )
            
            # 🔥 CRITICAL: Validate ws_message structure
            if not ws_message or not isinstance(ws_message, dict):
                return error_response(
                    error_message="Invalid WebSocket message structure",
                    detail_message=f"WebSocket message không hợp lệ (type: {type(ws_message).__name__})",
                    metadata={"tab_id": tab_id, "request_id": request_id, "ws_message_type": type(ws_message).__name__},
                    status_code=500,
                    show_traceback=False
                )
            
            # Try to serialize ws_message to JSON (validation)
            try:
                json_str = json.dumps(ws_message)
            except (TypeError, ValueError) as json_err:
                return error_response(
                    error_message="Failed to serialize WebSocket message to JSON",
                    detail_message=f"Không thể chuyển ws_message sang JSON. Lỗi: {str(json_err)}",
                    metadata={"tab_id": tab_id, "request_id": request_id, "json_error": str(json_err)},
                    status_code=500,
                    show_traceback=True
                )
            
            # Send message
            await port_manager.websocket.send_text(json_str)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
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
            
            # 🔥 CRITICAL: Validate response structure trước khi xử lý
            if not response or not isinstance(response, dict):
                return error_response(
                    error_message="Invalid response from wait_for_response",
                    detail_message=f"Response không hợp lệ (type: {type(response).__name__}). Có thể ZenTab extension không phản hồi đúng format.",
                    metadata={"tab_id": tab_id, "request_id": request_id, "response_type": type(response).__name__},
                    status_code=500,
                    show_traceback=False
                )
            
            # 🆕 FIX: Xử lý error response với status_hint từ wait_for_response
            if "error" in response:
                error_msg = response.get("error", "Unknown error")
                error_type = response.get("error_type", "UNKNOWN")
                status_hint = response.get("status_hint", 500)
                
                # Map error_type tới detail message phù hợp
                detail_messages = {
                    "TIMEOUT": f"Request timeout sau {response.get('timeout_seconds', 'N/A')} giây. Tab DeepSeek không phản hồi kịp thời.",
                    "COOLING_DOWN": "Tab đang trong trạng thái cooling down hoặc chưa sẵn sàng nhận request mới.",
                    "TAB_ERROR": "Tab gặp lỗi khi xử lý request.",
                    "EXCEPTION": f"Lỗi nội bộ: {error_msg}"
                }
                
                detail_message = detail_messages.get(error_type, error_msg)
                
                # Build metadata với thông tin đầy đủ
                error_metadata = {
                    "tab_id": tab_id,
                    "request_id": request_id,
                    "error_type": error_type
                }
                
                # Thêm thông tin bổ sung nếu có
                if "exception_class" in response:
                    error_metadata["exception_class"] = response["exception_class"]
                if "traceback_preview" in response:
                    error_metadata["traceback_preview"] = response["traceback_preview"][:200]
                
                return error_response(
                    error_message=f"Error from wait_for_response: {error_type}",
                    detail_message=detail_message,
                    metadata=error_metadata,
                    status_code=status_hint,
                    show_traceback=(error_type == "EXCEPTION")  # Chỉ show traceback cho EXCEPTION
                )
            
            port_manager.mark_request_completed(request_id)

            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=30.0))
            
            # 🔥 CRITICAL: _validate_and_fix_response có thể return error_response
            response = _validate_and_fix_response(response, request_id, is_fake=False)
            
            # 🔥 CRITICAL: Check nếu _validate_and_fix_response trả về StreamingResponse (là error)
            if isinstance(response, StreamingResponse):
                # Đây là error response từ _validate_and_fix_response
                return response
            
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
            
            if response.get("object") == "chat.completion.chunk":
                async def generate_real():
                    try:
                        yield f"data: {json.dumps(response)}\n\n"
                        yield "data: [DONE]\n\n"
                    except Exception as gen_error:
                        print(f"[API Route] ❌ Generator error: {gen_error}")
                
                return StreamingResponse(
                    generate_real(),
                    media_type="text/event-stream"
                )
            else:
                return response
            
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