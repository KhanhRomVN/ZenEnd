import re
import asyncio
import time
import uuid
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header

from config.settings import REQUEST_TIMEOUT
from models import ChatCompletionRequest
from .dependencies import verify_api_key
import uuid
import time


router = APIRouter()

def _convert_chunk_to_completion(chunk_data: dict) -> dict:
    """Convert chunk format to completion format for non-streaming requests"""
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

def _validate_and_fix_response(response: dict, request_id: str, is_fake: bool = False) -> dict:
    """
    Final validation và fix response format trước khi gửi cho Cline.
    Đảm bảo response luôn đúng format OpenAI completion.
    """
    import json
    
    source = "FAKE" if is_fake else "REAL"
    print(f"[API-VALIDATE] 🔍 Validating {source} response - requestId: {request_id}")
    print(f"[API-VALIDATE] 📊 Input type: {type(response)}")
    print(f"[API-VALIDATE] 📊 Input keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
    
    if not isinstance(response, dict):
        print(f"[API-VALIDATE] ❌ Response is not a dict!")
        raise HTTPException(status_code=500, detail="Invalid response format: not a dict")
    
    # Check required keys
    required_keys = ['id', 'object', 'created', 'model', 'choices']
    missing_keys = [key for key in required_keys if key not in response]
    
    if missing_keys:
        print(f"[API-VALIDATE] ❌ Missing required keys: {missing_keys}")
        print(f"[API-VALIDATE] 📝 Full response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Invalid response format: missing keys {missing_keys}"
        )
    
    # Check object type
    object_type = response.get('object')
    print(f"[API-VALIDATE] 📊 Object type: {object_type}")
    
    # 🆕 CRITICAL: Convert chunk to completion if needed
    if object_type == 'chat.completion.chunk':
        print(f"[API-VALIDATE] 🔄 Converting chunk format to completion format...")
        response = _convert_chunk_to_completion(response)
        print(f"[API-VALIDATE] ✅ Converted to completion format")
    elif object_type != 'chat.completion':
        print(f"[API-VALIDATE] ⚠️ Unexpected object type: {object_type}")
    
    # Check choices structure
    choices = response.get('choices', [])
    if not choices or len(choices) == 0:
        print(f"[API-VALIDATE] ❌ No choices in response!")
        raise HTTPException(status_code=500, detail="Invalid response: no choices")
    
    choice = choices[0]
    print(f"[API-VALIDATE] 📊 First choice keys: {list(choice.keys())}")
    
    # 🆕 CRITICAL: Ensure choice has 'message', not 'delta'
    if 'delta' in choice and 'message' not in choice:
        print(f"[API-VALIDATE] 🔄 Converting delta to message in choice...")
        delta = choice['delta']
        choice['message'] = {
            'role': delta.get('role', 'assistant'),
            'content': delta.get('content', '')
        }
        del choice['delta']
        print(f"[API-VALIDATE] ✅ Converted delta to message")
    
    if 'message' not in choice:
        print(f"[API-VALIDATE] ❌ Choice has no 'message' key!")
        print(f"[API-VALIDATE] 📝 Choice structure: {json.dumps(choice, indent=2, ensure_ascii=False)}")
        raise HTTPException(status_code=500, detail="Invalid response: choice has no message")
    
    message = choice['message']
    print(f"[API-VALIDATE] 📊 Message keys: {list(message.keys())}")
    print(f"[API-VALIDATE] 📊 Message role: {message.get('role')}")
    print(f"[API-VALIDATE] 📊 Message has content: {bool(message.get('content'))}")
    
    # Check content
    content = message.get('content')
    if content is None:
        print(f"[API-VALIDATE] ⚠️ Content is None, setting to empty string")
        message['content'] = ""
    
    content_type = type(content)
    content_length = len(str(content)) if content else 0
    print(f"[API-VALIDATE] 📊 Content type: {content_type}")
    print(f"[API-VALIDATE] 📊 Content length: {content_length}")
    
    if content_length > 0:
        print(f"[API-VALIDATE] 📝 Content preview (first 200 chars): {str(content)[:200]}")
    
    # Final validation summary
    print(f"[API-VALIDATE] ✅ Response validation completed successfully")
    print(f"[API-VALIDATE] 📝 Final response summary:")
    print(f"[API-VALIDATE]   - object: {response.get('object')}")
    print(f"[API-VALIDATE]   - model: {response.get('model')}")
    print(f"[API-VALIDATE]   - finish_reason: {choice.get('finish_reason')}")
    print(f"[API-VALIDATE]   - message.role: {message.get('role')}")
    print(f"[API-VALIDATE]   - message.content length: {len(str(message.get('content', '')))}")
    print(f"[API-VALIDATE]   - has tool_calls: {bool(message.get('tool_calls'))}")
    
    # 🆕 DEEP STRUCTURE COMPARISON
    print(f"[API-VALIDATE] 🔍 DEEP STRUCTURE ANALYSIS ({source}):")
    print(f"[API-VALIDATE]   - response type: {type(response).__name__}")
    print(f"[API-VALIDATE]   - choices type: {type(response.get('choices')).__name__}")
    print(f"[API-VALIDATE]   - first choice type: {type(choice).__name__}")
    print(f"[API-VALIDATE]   - message type: {type(message).__name__}")
    print(f"[API-VALIDATE]   - content type: {type(message.get('content')).__name__}")
    print(f"[API-VALIDATE]   - All response keys: {sorted(response.keys())}")
    print(f"[API-VALIDATE]   - All choice keys: {sorted(choice.keys())}")
    print(f"[API-VALIDATE]   - All message keys: {sorted(message.keys())}")
    
    # Check for unexpected keys that might break Cline
    unexpected_keys = set(response.keys()) - {'id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint'}
    if unexpected_keys:
        print(f"[API-VALIDATE] ⚠️ Unexpected response keys: {unexpected_keys}")
    
    unexpected_choice_keys = set(choice.keys()) - {'index', 'finish_reason', 'logprobs', 'message'}
    if unexpected_choice_keys:
        print(f"[API-VALIDATE] ⚠️ Unexpected choice keys: {unexpected_choice_keys}")
    
    unexpected_message_keys = set(message.keys()) - {'role', 'content', 'tool_calls'}
    if unexpected_message_keys:
        print(f"[API-VALIDATE] ⚠️ Unexpected message keys: {unexpected_message_keys}")
    
    return response
    """Convert chunk format to completion format for non-streaming requests"""
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
            print(f"[API] 📨 FAKE RESPONSE generated - requestId: {fake_request_id}")
            print(f"[API] 📊 Fake response type: {type(fake_response)}")
            print(f"[API] 📊 Fake response keys: {list(fake_response.keys()) if isinstance(fake_response, dict) else 'N/A'}")
            print(f"[API] 📝 RAW FAKE RESPONSE (no truncate):")
            print(json.dumps(fake_response, indent=2, ensure_ascii=False))
            print(f"[API] ═══════════════════════════════════════")
            
            # 🆕 LOG: Structure analysis for fake response
            if isinstance(fake_response, dict) and 'choices' in fake_response:
                fake_choice = fake_response['choices'][0] if fake_response['choices'] else {}
                fake_message = fake_choice.get('message', {})
                print(f"[API] 🔍 FAKE RESPONSE STRUCTURE DETAILS:")
                print(f"[API]   - response keys: {sorted(fake_response.keys())}")
                print(f"[API]   - choice keys: {sorted(fake_choice.keys())}")
                print(f"[API]   - message keys: {sorted(fake_message.keys())}")
                print(f"[API]   - message.content type: {type(fake_message.get('content')).__name__}")
                print(f"[API]   - message.content is None: {fake_message.get('content') is None}")
                print(f"[API]   - message.tool_calls: {fake_message.get('tool_calls')}")
                print(f"[API] ═══════════════════════════════════════")
            
            # Xử lý streaming response
            if request.stream and fake_response.get("object") == "chat.completion.chunk":
                # Trả về streaming response
                from fastapi.responses import StreamingResponse
                async def generate():
                    yield f"data: {json.dumps(fake_response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/plain"
                )
            else:
                # 🆕 CRITICAL: Final validation và fix response
                fake_response = _validate_and_fix_response(
                    fake_response, 
                    request_id=f"fake-{fake_request_id}", 
                    is_fake=True
                )
                
                print(f"[API] 🚀 SENDING FAKE RESPONSE TO CLINE (after validation)")
                print(f"[API] 📝 COMPLETE FINAL FAKE RESPONSE:")
                print(json.dumps(fake_response, indent=2, ensure_ascii=False))
                
                # 🆕 LOG: Final structure check before sending to Cline
                if isinstance(fake_response, dict) and 'choices' in fake_response:
                    fake_choice_final = fake_response['choices'][0] if fake_response['choices'] else {}
                    fake_message_final = fake_choice_final.get('message', {})
                    print(f"[API] 🔍 FINAL FAKE STRUCTURE CHECK:")
                    print(f"[API]   - Has 'choices'[0]['message']: {bool(fake_message_final)}")
                    print(f"[API]   - message keys: {list(fake_message_final.keys())}")
                    print(f"[API]   - message['content'] exists: {'content' in fake_message_final}")
                    print(f"[API]   - message['role'] exists: {'role' in fake_message_final}")
                    print(f"[API]   - Extra keys in message: {set(fake_message_final.keys()) - {'role', 'content', 'tool_calls'}}")
                
                print(f"[API] ═══════════════════════════════════════")
                
                return fake_response

        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        print(f"[API] Connection status: {conn_status}")
        
        # Kiểm tra WebSocket connection trước khi request tabs
        if not conn_status.get('websocket_connected') or not conn_status.get('websocket_open'):
            print(f"[API] ❌ WebSocket not connected - websocket_connected: {conn_status.get('websocket_connected')}, websocket_open: {conn_status.get('websocket_open')}")
            raise HTTPException(
                status_code=503,
                detail="WebSocket not connected. Please ensure ZenTab extension is connected to backend."
            )
        
        print(f"[API] ✅ WebSocket connected, requesting fresh tabs...")
        # Request danh sách tabs rảnh từ ZenTab với timeout 10s
        available_tabs = await port_manager.request_fresh_tabs(timeout=10.0)
        print(f"[API] Received {len(available_tabs)} tabs from ZenTab")
        
        if not available_tabs or len(available_tabs) == 0:
            print(f"[API] ❌ No tabs available from ZenTab")
            raise HTTPException(
                status_code=503,
                detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
            )

        # ZenTab chỉ trả về 1 tab duy nhất, lấy tab đầu tiên
        selected_tab = available_tabs[0]
        tab_id = selected_tab.get('tabId')
        
        print(f"[API] Selected tab: {selected_tab}")
        
        if not tab_id or not isinstance(tab_id, int) or tab_id <= 0:
            print(f"[API] ❌ Invalid tab ID received: {tab_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Invalid tab ID received from ZenTab: {tab_id}"
            )
        
        # Kiểm tra tab status
        tab_status = selected_tab.get('status', 'unknown')
        can_accept = selected_tab.get('canAccept', False)
        
        print(f"[API] Tab status: {tab_status}, canAccept: {can_accept}")
        
        if tab_status != 'free' or not can_accept:
            print(f"[API] ❌ Tab is not ready - status: {tab_status}, canAccept: {can_accept}")
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
            
            print(f"[API] 📨 RECEIVED RESPONSE from PortManager - requestId: {request_id}")
            print(f"[API] 📊 Response type: {type(response)}")
            print(f"[API] 📊 Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
            print(f"[API] 📝 COMPLETE RESPONSE (no truncate):")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print(f"[API] ═══════════════════════════════════════")
            
            # 🆕 LOG: Structure analysis for real response (BEFORE validation)
            if isinstance(response, dict) and 'choices' in response:
                real_choice = response['choices'][0] if response['choices'] else {}
                real_message = real_choice.get('message', {})
                print(f"[API] 🔍 REAL RESPONSE STRUCTURE DETAILS (BEFORE VALIDATION):")
                print(f"[API]   - response keys: {sorted(response.keys())}")
                print(f"[API]   - choice keys: {sorted(real_choice.keys())}")
                print(f"[API]   - message keys: {sorted(real_message.keys())}")
                print(f"[API]   - message.content type: {type(real_message.get('content')).__name__}")
                print(f"[API]   - message.content is None: {real_message.get('content') is None}")
                print(f"[API]   - message.tool_calls: {real_message.get('tool_calls')}")
                print(f"[API]   - Has 'delta' in choice: {'delta' in real_choice}")
                print(f"[API]   - object type: {response.get('object')}")
                print(f"[API] ═══════════════════════════════════════")
            
            if "error" in response:
                error_msg = response["error"]
                print(f"[API] ❌ Response contains error: {error_msg}")
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    raise HTTPException(
                        status_code=503,
                        detail=error_msg
                    )
                else:
                    raise HTTPException(status_code=500, detail=error_msg)
            
            from fastapi.responses import JSONResponse
            
            print(f"[API] 🔍 VALIDATING RESPONSE STRUCTURE...")
            required_keys = ['id', 'object', 'created', 'model', 'choices']
            for key in required_keys:
                has_key = key in response
                print(f"[API]   - Has '{key}': {has_key}")
            
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                print(f"[API] 📊 First choice structure:")
                print(f"[API]   - Choice keys: {list(choice.keys())}")
                print(f"[API]   - finish_reason: {choice.get('finish_reason')}")
                
                if 'message' in choice:
                    message = choice['message']
                    print(f"[API]   - Message keys: {list(message.keys())}")
                    print(f"[API]   - Message role: {message.get('role')}")
                    print(f"[API]   - Message content type: {type(message.get('content'))}")
                    print(f"[API]   - Message has tool_calls: {bool(message.get('tool_calls'))}")
                    content = message.get('content')
                    if content:
                        print(f"[API]   - Content length: {len(str(content))}")
                        print(f"[API]   - Content preview (first 200 chars): {str(content)[:200]}")
            
            print(f"[API] ✅ Response structure validation completed")
            
            port_manager.mark_request_completed(request_id)

            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=30.0))
            
            print(f"[API] 📨 REAL RESPONSE received from PortManager - requestId: {request_id}")
            print(f"[API] 📊 Real response type: {type(response)}")
            print(f"[API] 📝 RAW REAL RESPONSE (before validation):")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print(f"[API] ═══════════════════════════════════════")
            
            # 🆕 CRITICAL: Final validation và fix response
            response = _validate_and_fix_response(response, request_id, is_fake=False)
            
            print(f"[API] 🚀 SENDING REAL RESPONSE TO CLINE (after validation) - requestId: {request_id}")
            print(f"[API] 📊 Final response type: {type(response)}")
            print(f"[API] 📝 COMPLETE FINAL RESPONSE TO CLINE (no truncate):")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
            # 🆕 LOG: Final structure check before sending to Cline
            if isinstance(response, dict) and 'choices' in response:
                real_choice_final = response['choices'][0] if response['choices'] else {}
                real_message_final = real_choice_final.get('message', {})
                print(f"[API] 🔍 FINAL REAL STRUCTURE CHECK (AFTER VALIDATION):")
                print(f"[API]   - Has 'choices'[0]['message']: {bool(real_message_final)}")
                print(f"[API]   - message keys: {list(real_message_final.keys())}")
                print(f"[API]   - message['content'] exists: {'content' in real_message_final}")
                print(f"[API]   - message['role'] exists: {'role' in real_message_final}")
                print(f"[API]   - message['content'] type: {type(real_message_final.get('content')).__name__}")
                print(f"[API]   - message['content'] value: {repr(real_message_final.get('content'))[:100]}")
                print(f"[API]   - Extra keys in message: {set(real_message_final.keys()) - {'role', 'content', 'tool_calls'}}")
                print(f"[API]   - object type: {response.get('object')}")
                print(f"[API]   - finish_reason: {real_choice_final.get('finish_reason')}")
                
                # 🆕 COMPARE: So sánh với fake response structure
                print(f"[API] 📊 COMPARISON CHECK:")
                print(f"[API]   - Real response has same keys as fake? (checking structure similarity)")
                print(f"[API]   - Real message keys: {sorted(real_message_final.keys())}")
                print(f"[API]   - Expected message keys: ['content', 'role'] or ['content', 'role', 'tool_calls']")
            
            print(f"[API] ═══════════════════════════════════════")
            
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