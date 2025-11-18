"""
HTTP API routes
"""
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
from models import ChatCompletionRequest, TabStatus, TabState
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
                # 🆕 ENSURE: Fake response is in completion format for non-streaming
                if not request.stream and fake_response.get("object") == "chat.completion.chunk":
                    fake_response = _convert_chunk_to_completion(fake_response)
                return fake_response

        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        
        available_tabs = await port_manager.request_fresh_tabs()
        
        if not available_tabs:
            raise HTTPException(
                status_code=503,
                detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
            )

        free_tabs = [
            tab for tab in available_tabs 
            if tab.get('status') == 'free' and tab.get('canAccept', True)
        ]

        if not free_tabs:
            cooling_tabs = [
                tab for tab in available_tabs 
                if tab.get('status') == 'free' and not tab.get('canAccept', False)
            ]
            
            if cooling_tabs:
                for tab in cooling_tabs:
                    tab_id = tab['tabId']
                    cooling_time = tab.get('coolingDown', 0)
                    
                    await asyncio.sleep(2)
                    
                    refreshed_tabs = await port_manager.request_fresh_tabs()
                    refreshed_tab = next((t for t in refreshed_tabs if t['tabId'] == tab_id), None)
                    
                    if refreshed_tab and refreshed_tab.get('canAccept', False):
                        selected_tab = refreshed_tab
                        break

                else:
                    raise HTTPException(
                        status_code=503,
                        detail="All tabs are currently busy or cooling down. Please try again in a few seconds."
                    )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
                )
        else:
            selected_tab = free_tabs[0]

        tab_id = selected_tab['tabId']
        
        # 🆕 VALIDATE: Kiểm tra tab_id có hợp lệ không
        if not isinstance(tab_id, int) or tab_id <= 0:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid tab ID received: {tab_id}"
            )
        container_name = selected_tab.get('containerName', 'Unknown')

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

        tab_state = TabState(
            tab_id=tab_id,
            container_name=container_name,
            title=selected_tab.get('title', ''),
            url=selected_tab.get('url', '')
        )
        tab_state.mark_busy(request_id)
        port_manager.request_to_tab[request_id] = tab_id

        port_manager.temp_tab_states[tab_id] = tab_state
        
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "prompt": prompt,
            "requestId": request_id
        }
        
        try:
            await port_manager.websocket.send(json.dumps(ws_message))
        except Exception as e:
            tab_state.mark_free()
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
            
            from fastapi.responses import JSONResponse
            
            required_keys = ['id', 'object', 'created', 'model', 'choices']
            for key in required_keys:
                has_key = key in response
            
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                
                if 'message' in choice:
                    message = choice['message']
                    content = message.get('content')
            
            # 🔧 CRITICAL FIX: KHÔNG cleanup temp_tab_state ngay lập tức
            # Tab state sẽ tự cleanup sau 60s hoặc khi có request mới
            # Điều này cho phép WebSocket handler có thời gian xử lý duplicate messages
            
            # 🆕 ENHANCED: Cleanup ngay lập tức + schedule backup cleanup
            port_manager.mark_request_completed(request_id)

            # Cleanup temp tab state sau 10s (cho WebSocket handler xử lý xong)
            asyncio.create_task(port_manager.schedule_temp_tab_cleanup(tab_id, delay=10.0))

            # Schedule cleanup request mapping sau 30 giây (backup)
            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=30.0))
            
            return response
            
        except HTTPException as he:
            # Cleanup temp tab state ngay khi có lỗi HTTP
            port_manager.cleanup_temp_tab_state(tab_id)
            
            # 🆕 THÊM: Đánh dấu request đã processed để chặn duplicates
            port_manager.mark_request_processed(request_id)
            
            # Schedule cleanup request mapping
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
            # Cleanup temp tab state ngay khi có exception
            port_manager.cleanup_temp_tab_state(tab_id)
            
            # 🆕 THÊM: Đánh dấu request đã processed để chặn duplicates
            port_manager.mark_request_processed(request_id)
            
            # Schedule cleanup request mapping
            asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=10.0))
            
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # 🔧 CRITICAL FIX: KHÔNG cleanup temp_tab_state trong finally
            # Vì success case cần giữ state để WebSocket handler xử lý
            # Chỉ cleanup trong error cases (đã xử lý ở except blocks)
            pass
    
    app.include_router(router)