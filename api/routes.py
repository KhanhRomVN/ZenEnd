"""
HTTP API routes
"""
import time
import uuid
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header

from config.settings import REQUEST_TIMEOUT
from models import ChatCompletionRequest, TabStatus, TabState
from .dependencies import verify_api_key


router = APIRouter()


def setup_routes(app, port_manager):
    """Setup routes với port_manager dependency"""
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
        """
        OpenAI-compatible chat completions endpoint với cơ chế chọn tab thông minh
        """
        
        # 1. Validate model - chấp nhận cả deepseek-chat và deepseek-coder
        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        
        for tab_id, tab_state in sorted(port_manager.global_tab_pool.items()):
            status_icon = {
                TabStatus.FREE: "🟢",
                TabStatus.BUSY: "🔵",
                TabStatus.ERROR: "🔴",
                TabStatus.NOT_FOUND: "⚫"
            }.get(tab_state.status, "⚪")
            
            time_since_use = time.time() - tab_state.last_used if tab_state.last_used > 0 else float('inf')
            time_str = f"{time_since_use:.1f}s ago" if time_since_use != float('inf') else "never used"
            
            can_accept = "✓ Ready" if tab_state.can_accept_request() else "✗ Not ready"
        
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
            raise HTTPException(
                status_code=503,
                detail="No free tabs available. Please try again in a few seconds."
            )

        # Chọn tab đầu tiên từ danh sách free
        selected_tab = free_tabs[0]
        tab_id = selected_tab['tabId']
        container_name = selected_tab.get('containerName', 'Unknown')

        # 4. Tạo request ID và gửi prompt
        request_id = f"api-{uuid.uuid4().hex[:16]}"

        # Extract user message (lấy message cuối cùng từ user)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")

        prompt = user_messages[-1].content


        # 5. Đánh dấu tab BUSY và track request (tạo TabState tạm thời)
        tab_state = TabState(
            tab_id=tab_id,
            container_name=container_name,
            title=selected_tab.get('title', ''),
            url=selected_tab.get('url', '')
        )
        tab_state.mark_busy(request_id)
        port_manager.request_to_tab[request_id] = tab_id

        # Lưu tab state tạm thời cho request này
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
            # Gửi thất bại: đánh dấu tab free
            tab_state.mark_free()
            port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=f"Failed to send prompt: {str(e)}")
        
        # 5. Chờ response từ ZenTab
        try:
            response = await port_manager.wait_for_response(request_id, REQUEST_TIMEOUT)
            
            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])
            
            return response
            
        except HTTPException:
            # Đã xử lý timeout trong wait_for_response
            raise
        except Exception as e:
            port_manager.cleanup_temp_tab_state(tab_id)
            port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            port_manager.cleanup_temp_tab_state(tab_id)
    
    # Register router
    app.include_router(router)