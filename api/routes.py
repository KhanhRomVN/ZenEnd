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
    print(f"[Routes] 🔧 Setting up routes with PortManager: {id(port_manager)}")

    @router.post("/v1/chat/completions")
    async def chat_completions(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key)
    ):
        """
        OpenAI-compatible chat completions endpoint với cơ chế chọn tab thông minh
        """
        print("\n" + "="*80)
        print(f"[API] 📨 NEW REQUEST at {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        
        # 1. Validate model
        if request.model != "deepseek-web":
            raise HTTPException(status_code=400, detail=f"Model '{request.model}' not supported. Only 'deepseek-web' is available.")
        
        # LOG: Chi tiết về WebSocket và tabs
        print("\n[API] 🔍 SYSTEM STATUS CHECK:")
        print(f"[API]   - Calling port_manager.get_connection_status()...")
        
        # 🆕 DEBUG: Chi tiết connection state
        conn_status = port_manager.get_connection_status()
        
        print(f"[API]   - Got connection status: {conn_status}")
        print(f"├─ WebSocket object exists: {conn_status['websocket_connected']}")
        print(f"├─ WebSocket open: {conn_status['websocket_open']}")
        print(f"├─ Port: {conn_status['port']}")
        print(f"├─ Total tabs available: {conn_status['total_tabs']}")
        print(f"├─ Free tabs: {conn_status['free_tabs']}")
        print(f"└─ Busy tabs: {conn_status['busy_tabs']}")
        
        # 🆕 LOG: Chi tiết từng tab trong global pool
        print(f"\n[API] 📋 GLOBAL TAB POOL ({len(port_manager.global_tab_pool)} tabs):")
        for tab_id, tab_state in sorted(port_manager.global_tab_pool.items()):
            status_icon = {
                TabStatus.FREE: "🟢",
                TabStatus.BUSY: "🔵",
                TabStatus.ERROR: "🔴",
                TabStatus.NOT_FOUND: "⚫"
            }.get(tab_state.status, "⚪")
            
            # Tính thời gian từ lần sử dụng cuối
            time_since_use = time.time() - tab_state.last_used if tab_state.last_used > 0 else float('inf')
            time_str = f"{time_since_use:.1f}s ago" if time_since_use != float('inf') else "never used"
            
            # Check xem tab có thể nhận request không
            can_accept = "✓ Ready" if tab_state.can_accept_request() else "✗ Not ready"
            
            print(f"  {status_icon} Tab {tab_id} ({tab_state.container_name})")
            print(f"     Status: {tab_state.status.value} | Last used: {time_str}")
            print(f"     {can_accept} | Errors: {tab_state.error_count}")
            if tab_state.current_request_id:
                print(f"     Current request: {tab_state.current_request_id}")
        
        # 2. Yêu cầu danh sách tabs mới từ ZenTab
        print("\n[API] 🎯 REQUESTING FRESH TABS FROM ZENTAB...")

        # 🆕 FIX: Luôn yêu cầu danh sách tabs mới từ ZenTab
        available_tabs = await port_manager.request_fresh_tabs()
        if not available_tabs:
            print("[API] ❌ No tabs available from ZenTab")
            raise HTTPException(
                status_code=503,
                detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
            )

        print(f"[API] ✅ Received {len(available_tabs)} tabs from ZenTab")

        # 3. Chọn một tab free từ danh sách mới
        print("\n[API] 🔍 SELECTING FREE TAB FROM FRESH LIST...")

        # Lọc tabs free (status = FREE và có thể nhận request)
        free_tabs = [
            tab for tab in available_tabs 
            if tab.get('status') == 'free' and tab.get('canAccept', True)
        ]

        if not free_tabs:
            print("[API] ❌ No free tabs available in fresh list")
            raise HTTPException(
                status_code=503,
                detail="No free tabs available. Please try again in a few seconds."
            )

        # Chọn tab đầu tiên từ danh sách free
        selected_tab = free_tabs[0]
        tab_id = selected_tab['tabId']
        container_name = selected_tab.get('containerName', 'Unknown')

        print(f"[API] ✅ Selected tab {tab_id} ({container_name})")

        # 4. Tạo request ID và gửi prompt
        request_id = f"api-{uuid.uuid4().hex[:16]}"

        # Extract user message (lấy message cuối cùng từ user)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")

        prompt = user_messages[-1].content

        print(f"[API] 🎯 Using fresh tab {tab_id} ({container_name})")

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
            print(f"\n[API] 📤 PROMPT SENT:")
            print(f"  ├─ Request ID: {request_id}")
            print(f"  ├─ Target: Tab {tab_id}")
            print(f"  └─ Prompt length: {len(prompt)} chars")
            print(f"\n[API] ⏳ Waiting for response (timeout: {REQUEST_TIMEOUT}s)...")
        except Exception as e:
            # Gửi thất bại: đánh dấu tab free
            tab_state.mark_free()
            port_manager.request_to_tab.pop(request_id, None)
            print(f"\n[API] ❌ FAILED TO SEND PROMPT: {str(e)}")
            print("="*80 + "\n")
            raise HTTPException(status_code=500, detail=f"Failed to send prompt: {str(e)}")
        
        # 5. Chờ response từ ZenTab
        try:
            response = await port_manager.wait_for_response(request_id, REQUEST_TIMEOUT)
            
            if "error" in response:
                print(f"\n[API] ❌ ERROR RESPONSE:")
                print(f"  └─ {response['error']}")
                print("="*80 + "\n")
                raise HTTPException(status_code=500, detail=response["error"])
            
            print(f"\n[API] ✅ SUCCESS!")
            print(f"  ├─ Request ID: {request_id}")
            print(f"  ├─ Response received from Tab {tab_id}")
            print(f"  └─ Response length: {len(str(response))} chars")
            print("="*80 + "\n")
            
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