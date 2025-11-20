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

def _log_response_fields_extraction(response: dict, stage: str = "raw", is_fake: bool = False):
    """Log chi tiết các field được extract từ response"""
    source = "FAKE" if is_fake else "REAL"
    print(f"\n[FIELD EXTRACTION - {stage} - {source}]")
    print(f"{'-'*80}")
    
    # Log top-level fields
    print(f"Top-level fields:")
    print(f"  id: {response.get('id', 'N/A')}")
    print(f"  object: {response.get('object', 'N/A')}")
    print(f"  created: {response.get('created', 'N/A')}")
    print(f"  model: {response.get('model', 'N/A')}")
    print(f"  system_fingerprint: {response.get('system_fingerprint', 'N/A')}")
    
    # Log choices extraction
    original_choices = response.get('choices', [])
    print(f"\nChoices extraction:")
    print(f"  Total choices: {len(original_choices)}")
    
    if original_choices:
        original_choice = original_choices[0]
        print(f"  Choice[0] index: {original_choice.get('index', 'N/A')}")
        print(f"  Choice[0] finish_reason: {original_choice.get('finish_reason', 'N/A')}")
        print(f"  Choice[0] logprobs: {original_choice.get('logprobs', 'N/A')}")
        
        # 🆕 Log structure type (message vs delta)
        has_message = 'message' in original_choice
        has_delta = 'delta' in original_choice
        print(f"\nStructure type:")
        print(f"  has 'message': {has_message}")
        print(f"  has 'delta': {has_delta}")
        
        # Log message/delta extraction
        message_data = original_choice.get('message') or original_choice.get('delta', {})
        print(f"\nMessage/Delta extraction:")
        print(f"  role: {message_data.get('role', 'N/A')}")
        content = message_data.get('content', '')
        print(f"  content length: {len(content) if content else 0} chars")
        if content:
            content_preview = content[:150] + "..." if len(content) > 150 else content
            print(f"  content preview: {content_preview}")
        print(f"  tool_calls: {message_data.get('tool_calls', 'None')}")
    
    # Log usage extraction
    original_usage = response.get('usage', {})
    print(f"\nUsage extraction:")
    print(f"  prompt_tokens: {original_usage.get('prompt_tokens', 0)}")
    print(f"  completion_tokens: {original_usage.get('completion_tokens', 0)}")
    print(f"  total_tokens: {original_usage.get('total_tokens', 0)}")
    
    print(f"{'-'*80}\n")

def _log_final_response(response: dict, is_fake: bool = False):
    """Log final response để so sánh fake vs real response"""
    response_type = "FAKE" if is_fake else "REAL"
    
    print(f"\n{'='*80}")
    print(f"[FINAL RESPONSE - {response_type}]")
    print(f"{'='*80}")
    
    # Log response ID và metadata
    print(f"ID: {response.get('id', 'N/A')}")
    print(f"Model: {response.get('model', 'N/A')}")
    print(f"Object: {response.get('object', 'N/A')}")
    print(f"Created: {response.get('created', 'N/A')}")
    
    # Log choices details
    choices = response.get('choices', [])
    print(f"\nChoices count: {len(choices)}")
    
    for i, choice in enumerate(choices):
        print(f"\n--- Choice {i} ---")
        print(f"Index: {choice.get('index', 'N/A')}")
        print(f"Finish reason: {choice.get('finish_reason', 'N/A')}")
            
        # 🆕 Log structure type
        has_message = 'message' in choice
        has_delta = 'delta' in choice
        print(f"Structure: message={has_message}, delta={has_delta}")
            
        # Extract từ message hoặc delta
        message_data = choice.get('message') or choice.get('delta', {})
        role = message_data.get('role', 'N/A')
        content = message_data.get('content', '')
        tool_calls = message_data.get('tool_calls')
            
        print(f"Role: {role}")
        print(f"Content length: {len(content) if content else 0} chars")
            
        if content:
            content_preview = content[:200] + "..." if len(content) > 200 else content
            print(f"Content preview: {content_preview}")
            
        # Only log tool_calls nếu tồn tại
        if tool_calls:
            print(f"Tool calls count: {len(tool_calls)}")
            for j, tool in enumerate(tool_calls):
                tool_name = tool.get('function', {}).get('name', 'N/A')
                print(f"  Tool {j}: {tool_name}")
        else:
            print(f"Tool calls: None")

    # Log usage
    usage = response.get('usage', {})
    print(f"\nUsage:")
    print(f"  Prompt tokens: {usage.get('prompt_tokens', 0)}")
    print(f"  Completion tokens: {usage.get('completion_tokens', 0)}")
    print(f"  Total tokens: {usage.get('total_tokens', 0)}")
    
    # 🆕 Log full JSON (formatted) - dễ copy/paste
    print(f"\n--- Full JSON Response ---")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print(f"{'='*80}\n")

from config.settings import REQUEST_TIMEOUT
from models import ChatCompletionRequest
from .dependencies import verify_api_key
import uuid
import time


router = APIRouter()

def _validate_and_fix_response(response: dict, request_id: str, is_fake: bool = False) -> dict:
    """
    Rebuild response từ ZenTab thành clean OpenAI completion format.
    Extract từng field và tạo lại object mới thay vì parse phức tạp.
    """
    
    if not isinstance(response, dict):
        raise HTTPException(status_code=500, detail="Invalid response format: not a dict")
    
    # 🆕 LOG: Raw response fields extraction (với flag is_fake)
    _log_response_fields_extraction(response, stage="raw_from_provider", is_fake=is_fake)
    
    # Extract top-level fields
    response_id = response.get('id', f'chatcmpl-{request_id}')
    object_type = response.get('object', 'chat.completion.chunk')
    created = response.get('created', int(time.time()))
    model = response.get('model', 'deepseek-chat')
    system_fingerprint = response.get('system_fingerprint', f'fp_{uuid.uuid4().hex[:8]}')
    
    print(f"[EXTRACTED TOP-LEVEL FIELDS]")
    print(f"  response_id: {response_id}")
    print(f"  object_type: {object_type}")
    print(f"  created: {created}")
    print(f"  model: {model}")
    print(f"  system_fingerprint: {system_fingerprint}\n")
    
    # Extract choices array
    original_choices = response.get('choices', [])
    if not original_choices or len(original_choices) == 0:
        raise HTTPException(status_code=500, detail="Invalid response: no choices")
    
    # Extract first choice
    original_choice = original_choices[0]
    choice_index = original_choice.get('index', 0)
    finish_reason = original_choice.get('finish_reason', 'stop')
    logprobs = original_choice.get('logprobs', None)
    
    print(f"[EXTRACTED CHOICE[0] FIELDS]")
    print(f"  choice_index: {choice_index}")
    print(f"  finish_reason: {finish_reason}")
    print(f"  logprobs: {logprobs}\n")
    
    # Extract message/delta (ZenTab có thể trả về 'delta' hoặc 'message')
    has_message = 'message' in original_choice
    has_delta = 'delta' in original_choice
    message_data = original_choice.get('message') or original_choice.get('delta', {})
    
    role = message_data.get('role', 'assistant')
    raw_content = message_data.get('content', '')
    tool_calls = message_data.get('tool_calls', None)
    
    # 🆕 FIX: Decode escaped newlines nếu content là string với \\n
    content = raw_content
    if isinstance(raw_content, str) and '\\n' in raw_content:
        # Replace escaped newlines với real newlines
        content = raw_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
        print(f"[CONTENT FIX] Decoded {raw_content.count(chr(92) + 'n')} escaped newlines")
    
    print(f"[EXTRACTED MESSAGE/DELTA FIELDS]")
    print(f"  has_message: {has_message}")
    print(f"  has_delta: {has_delta}")
    print(f"  role: {role}")
    print(f"  raw_content length: {len(raw_content) if raw_content else 0} chars")
    print(f"  decoded_content length: {len(content) if content else 0} chars")
    if content:
        content_preview = content[:150] + "..." if len(content) > 150 else content
        print(f"  content preview: {content_preview}")
    print(f"  tool_calls: {tool_calls}\n")
    
    # Extract usage
    original_usage = response.get('usage', {})
    prompt_tokens = original_usage.get('prompt_tokens', 0)
    completion_tokens = original_usage.get('completion_tokens', 0)
    total_tokens = original_usage.get('total_tokens', 0)
    
    print(f"[EXTRACTED USAGE FIELDS]")
    print(f"  prompt_tokens: {prompt_tokens}")
    print(f"  completion_tokens: {completion_tokens}")
    print(f"  total_tokens: {total_tokens}\n")
    
    # 🆕 Rebuild: Fake dùng 'message' + 'tool_calls', Real dùng 'delta' (không tool_calls)
    if is_fake:
        # Fake response: dùng 'message' + 'tool_calls'
        choice_data = {
            'index': choice_index,
            'message': {
                'role': role,
                'content': content,
                'tool_calls': tool_calls
            },
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }
        print(f"[BUILD MODE] Using 'message' + 'tool_calls' (FAKE)")
    else:
        # Real response: dùng 'delta' (không tool_calls) - delta phải đứng TRƯỚC finish_reason
        choice_data = {
            'index': choice_index,
            'delta': {
                'role': role,
                'content': content
            },
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }
        print(f"[BUILD MODE] Using 'delta' without 'tool_calls' (REAL)\n")
    
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
    
    # 🆕 LOG: Rebuilt response structure
    print(f"[REBUILT CLEAN RESPONSE - JSON]")
    print(json.dumps(clean_response, indent=2, ensure_ascii=False))
    print()
    
    return clean_response

def _build_choice_for_response(choice_index: int, finish_reason: str, logprobs, 
                               role: str, content: str, tool_calls, is_fake: bool) -> dict:
    """
    Build choice object - structure khác nhau cho fake vs real
    - Fake: dùng 'message' field + có 'tool_calls'
    - Real: dùng 'delta' field + không có 'tool_calls' (delta phải đứng TRƯỚC finish_reason)
    """
    if is_fake:
        return {
            'index': choice_index,
            'message': {
                'role': role,
                'content': content,
                'tool_calls': tool_calls
            },
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }
    else:
        return {
            'index': choice_index,
            'delta': {
                'role': role,
                'content': content
            },
            'finish_reason': finish_reason,
            'logprobs': logprobs
        }

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
        
        if is_fake_mode_enabled():
            fake_response = create_fake_response(
                model=request.model, 
                messages=request.messages,
                stream=request.stream if hasattr(request, 'stream') else False
            )
            
            fake_request_id = uuid.uuid4().hex[:16]
            
            # 🆕 LOG: Raw fake response từ create_fake_response
            print(f"\n[RAW FAKE RESPONSE - PRE-VALIDATION]")
            print(f"{'='*80}")
            print(json.dumps(fake_response, indent=2, ensure_ascii=False))
            print(f"{'='*80}\n")
            
            # Xử lý streaming response
            if request.stream and fake_response.get("object") == "chat.completion.chunk":
                # Trả về streaming response
                from fastapi.responses import StreamingResponse
                async def generate():
                    yield f"data: {json.dumps(fake_response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/event-stream"
                )
            else:
                # 🆕 FIX: Luôn pass qua validation để có full logging
                try:
                    fake_response = _validate_and_fix_response(
                        fake_response, 
                        request_id=f"fake-{fake_request_id}", 
                        is_fake=True
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to validate fake response: {e}")
                    # Tạo fallback nếu validation fail
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
                
                # 🆕 LOG: Final fake response sau khi validate
                _log_final_response(fake_response, is_fake=True)
                
                return fake_response

        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        
        # Kiểm tra WebSocket connection trước khi request tabs
        if not conn_status.get('websocket_connected') or not conn_status.get('websocket_open'):
            raise HTTPException(
                status_code=503,
                detail="WebSocket not connected. Please ensure ZenTab extension is connected to backend."
            )
        
        # Request danh sách tabs rảnh từ ZenTab với timeout 10s
        available_tabs = await port_manager.request_fresh_tabs(timeout=10.0)
        
        if not available_tabs or len(available_tabs) == 0:
            raise HTTPException(
                status_code=503,
                detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
            )

        # ZenTab chỉ trả về 1 tab duy nhất, lấy tab đầu tiên
        selected_tab = available_tabs[0]
        tab_id = selected_tab.get('tabId')
        
        if not tab_id or not isinstance(tab_id, int) or tab_id <= 0:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid tab ID received from ZenTab: {tab_id}"
            )
        
        # Kiểm tra tab status
        tab_status = selected_tab.get('status', 'unknown')
        can_accept = selected_tab.get('canAccept', False)
        
        if tab_status != 'free' or not can_accept:
            raise HTTPException(
                status_code=503,
                detail=f"Tab is not ready to accept requests. Status: {tab_status}, Can accept: {can_accept}"
            )

        request_id = f"api-{uuid.uuid4().hex[:16]}"

        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")

        raw_content = user_messages[-1].content
        
        if isinstance(raw_content, list):
            text_parts = []
            for item in raw_content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        text_parts.append("[IMAGE - Not supported]")
            
            prompt = "\n\n".join(text_parts)
        else:
            prompt = raw_content

        port_manager.request_to_tab[request_id] = tab_id
        
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "prompt": prompt,
            "requestId": request_id
        }
        
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
            
            # Final validation và fix response
            response = _validate_and_fix_response(response, request_id, is_fake=False)
            
            # LOG: Final real response
            _log_final_response(response, is_fake=False)
            
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
                
                # 🆕 LOG: Fallback response
                _log_final_response(fallback_response, is_fake=False)
                
                return fallback_response
        except Exception as e:
            port_manager.mark_request_processed(request_id)
            
            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=10.0))
            
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            pass
    
    app.include_router(router)