import re
import asyncio
from api.fake_response import create_fake_response
import time
import uuid
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header

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
    Kiểm tra xem có <task></task> trong MESSAGE CUỐI CÙNG không.
    Trả về True nếu đây là task mới.
    """
    if not messages:
        return False
    
    latest_msg = messages[-1]
    content = latest_msg.content
    if isinstance(content, str):
        if '<task>' in content and '</task>' in content:
            return True
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if '<task>' in text and '</task>' in text:
                    return True
    return False

def _validate_and_fix_response(response: dict, request_id: str, is_fake: bool = False) -> dict:
    """
    Rebuild response từ ZenTab thành clean OpenAI completion format.
    Extract từng field và tạo lại object mới thay vì parse phức tạp.
    """
    if not isinstance(response, dict):
        raise HTTPException(status_code=500, detail="Invalid response format: not a dict")
    
    # Extract top-level fields
    response_id = response.get('id', f'chatcmpl-{request_id}')
    object_type = response.get('object', 'chat.completion.chunk')
    created = response.get('created', int(time.time()))
    model = response.get('model', 'deepseek-chat')
    system_fingerprint = response.get('system_fingerprint', f'fp_{uuid.uuid4().hex[:8]}')
    
    # Extract choices array
    original_choices = response.get('choices', [])
    if not original_choices or len(original_choices) == 0:
        raise HTTPException(status_code=500, detail="Invalid response: no choices")
    
    # Extract first choice
    original_choice = original_choices[0]
    choice_index = original_choice.get('index', 0)
    finish_reason = original_choice.get('finish_reason', 'stop')
    logprobs = original_choice.get('logprobs', None)
    
    # Extract message/delta
    message_data = original_choice.get('message') or original_choice.get('delta', {})
    role = message_data.get('role', 'assistant')
    raw_content = message_data.get('content', '')
    tool_calls = message_data.get('tool_calls', None)
    
    # Fix: Decode escaped newlines
    content = raw_content
    if isinstance(raw_content, str) and '\\n' in raw_content:
        content = raw_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    
    # Extract usage
    original_usage = response.get('usage', {})
    prompt_tokens = original_usage.get('prompt_tokens', 0)
    completion_tokens = original_usage.get('completion_tokens', 0)
    total_tokens = original_usage.get('total_tokens', 0)
    
    # Rebuild: Fake dùng 'message' + 'tool_calls', Real dùng 'delta'
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
    
    # Rebuild clean response
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

from config.settings import REQUEST_TIMEOUT
from models import ChatCompletionRequest
from .dependencies import verify_api_key
import uuid
import time

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
                },
                {
                    "id": "deepseek-coder",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "zenend"
                }
            ]
        }

    @router.post("/v1/chat/completions")
    async def chat_completions(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key)
    ):
        from api.fake_response import is_fake_mode_enabled, create_fake_response
        from fastapi.responses import StreamingResponse
        
        if is_fake_mode_enabled():
            fake_response = create_fake_response(
                model=request.model, 
                messages=request.messages,
                stream=request.stream if hasattr(request, 'stream') else False
            )
            
            fake_request_id = uuid.uuid4().hex[:16]
            
            if request.stream and fake_response.get("object") == "chat.completion.chunk":
                async def generate():
                    yield f"data: {json.dumps(fake_response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/event-stream"
                )
            else:
                try:
                    fake_response = _validate_and_fix_response(
                        fake_response, 
                        request_id=f"fake-{fake_request_id}", 
                        is_fake=True
                    )
                except Exception as e:
                    fake_response = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Fake response validation error"
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
                
                return fake_response

        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        
        if not conn_status.get('websocket_connected') or not conn_status.get('websocket_open'):
            raise HTTPException(
                status_code=503,
                detail="WebSocket not connected. Please ensure ZenTab extension is connected to backend."
            )
        
        # Extract folder_path và detect new task
        folder_path = _extract_folder_path(request.messages)
        is_new_task = _detect_new_task(request.messages)

        # Chọn tab dựa trên new task vs existing task
        if is_new_task:
            # New task: request tất cả tabs rảnh
            available_tabs = await port_manager.request_fresh_tabs(timeout=10.0)
            
            if not available_tabs or len(available_tabs) == 0:
                raise HTTPException(
                    status_code=503,
                    detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
                )
            
            # Nếu có folder_path, gửi WS để xóa liên kết cũ
            if folder_path:
                cleanup_msg = {
                    "type": "cleanupFolderLink",
                    "folderPath": folder_path,
                    "timestamp": int(time.time() * 1000)
                }
                try:
                    await port_manager.websocket.send(json.dumps(cleanup_msg))
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
            
            selected_tab = available_tabs[0]
        else:
            # Existing task: tìm tab có folder_path khớp
            if not folder_path:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot find folder_path in request. Please ensure the task context is included."
                )
            
            folder_tabs = await port_manager.request_tabs_by_folder(folder_path, timeout=10.0)
            
            if not folder_tabs or len(folder_tabs) == 0:
                raise HTTPException(
                    status_code=503,
                    detail=f"No tabs linked to folder '{folder_path}'. Please start a new task first."
                )
            
            selected_tab = folder_tabs[0]
        
        tab_id = selected_tab.get('tabId')
        
        if not tab_id or not isinstance(tab_id, int) or tab_id <= 0:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid tab ID received from ZenTab: {tab_id}"
            )
        
        tab_status = selected_tab.get('status', 'unknown')
        can_accept = selected_tab.get('canAccept', False)
        
        if tab_status != 'free' or not can_accept:
            raise HTTPException(
                status_code=503,
                detail=f"Tab is not ready to accept requests. Status: {tab_status}, Can accept: {can_accept}"
            )

        request_id = f"api-{uuid.uuid4().hex[:16]}"

        # Extract BOTH system prompt and user messages
        system_messages = [msg for msg in request.messages if msg.role == "system"]
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")

        # Extract system prompt
        system_prompt = ""
        if system_messages:
            system_content = system_messages[0].content
            if isinstance(system_content, str):
                system_prompt = system_content
            elif isinstance(system_content, list):
                text_parts = []
                for item in system_content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                system_prompt = "\n\n".join(text_parts)
        
        # Extract user message
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
        
        # Send prompt với folder_path handling
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "systemPrompt": system_prompt,
            "userPrompt": user_prompt,
            "requestId": request_id,
            "isNewTask": is_new_task
        }
        
        # Chỉ gửi folder_path khi là new task
        if is_new_task and folder_path:
            ws_message["folderPath"] = folder_path
        
        try:
            await port_manager.websocket.send(json.dumps(ws_message))
        except Exception as e:
            port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=f"Failed to send prompt: {str(e)}")
        
        try:
            response = await port_manager.wait_for_response(request_id, REQUEST_TIMEOUT)
            
            if "error" in response:
                error_msg = response["error"]
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    raise HTTPException(
                        status_code=503,
                        detail=error_msg
                    )
                else:
                    raise HTTPException(status_code=500, detail=error_msg)
            
            port_manager.mark_request_completed(request_id)

            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=30.0))
            
            response = _validate_and_fix_response(response, request_id, is_fake=False)
            
            # Wrap real response trong StreamingResponse
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
                raise
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
            
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            pass
    
    app.include_router(router)