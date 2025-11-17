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
from models import ChatCompletionRequest, TabStatus
from .dependencies import verify_api_key


router = APIRouter()


def setup_routes(app, port_manager):
    """Setup routes với port_manager dependency"""
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint chi tiết"""
        detailed_status = port_manager.get_detailed_status()
        return {
            "status": "healthy",
            "ports": {
                "total": len(port_manager.ports),
                "connected": port_manager.get_connected_count(),
                "busy_tabs": port_manager.get_busy_count(),
                "free_tabs": port_manager.get_total_free_tabs(),
            },
            "detailed_status": detailed_status
        }

    @router.get("/v1/status/detailed")
    async def get_detailed_status(api_key: str = Depends(verify_api_key)):
        """Get detailed real-time status of all ports and tabs"""
        # Build detailed status
        ports_detail = []
        
        for port, port_state in sorted(port_manager.ports.items()):
            if not port_state.websocket:
                ports_detail.append({
                    "port": port,
                    "connected": False,
                    "tabs": []
                })
                continue
            
            tabs_detail = []
            for tab_id, tab_state in sorted(port_state.tabs.items()):
                tabs_detail.append({
                    "tab_id": tab_id,
                    "container_name": tab_state.container_name,
                    "title": tab_state.title,
                    "status": tab_state.status.value,
                    "can_accept_request": tab_state.can_accept_request(),
                    "error_count": tab_state.error_count,
                    "last_used_seconds_ago": time.time() - tab_state.last_used if tab_state.last_used > 0 else None,
                    "current_request_id": tab_state.current_request_id
                })
            
            ports_detail.append({
                "port": port,
                "connected": True,
                "tabs": tabs_detail,
                "summary": port_state.get_tab_status_summary()
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "connected_ports": port_manager.get_connected_count(),
                "total_ports": len(port_manager.ports),
                "total_tabs": sum(len(ps.tabs) for ps in port_manager.ports.values()),
                "free_tabs": port_manager.get_total_free_tabs(),
                "busy_tabs": port_manager.get_busy_count()
            },
            "ports": ports_detail
        }

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
        
        # 🆕 LOG: Chi tiết về tất cả ports và tabs
        print("\n[API] 🔍 SYSTEM STATUS CHECK:")
        print(f"├─ Connected WebSocket ports: {port_manager.get_connected_count()}/{len(port_manager.ports)}")
        print(f"├─ Total tabs available: {sum(len(ps.tabs) for ps in port_manager.ports.values())}")
        print(f"├─ Free tabs: {port_manager.get_total_free_tabs()}")
        print(f"└─ Busy tabs: {port_manager.get_busy_count()}")
        
        print("\n[API] 📊 DETAILED PORT STATUS:")
        for port, port_state in sorted(port_manager.ports.items()):
            if not port_state.websocket:
                print(f"  Port {port}: ❌ DISCONNECTED")
                continue
                
            status_summary = port_state.get_tab_status_summary()
            print(f"  Port {port}: ✅ CONNECTED")
            print(f"    ├─ Total tabs: {status_summary['total_tabs']}")
            print(f"    ├─ Free: {status_summary['free_tabs']}")
            print(f"    ├─ Busy: {status_summary['busy_tabs']}")
            print(f"    ├─ Error: {status_summary['error_tabs']}")
            print(f"    └─ Not Found: {status_summary['not_found_tabs']}")
            
            # 🆕 LOG: Chi tiết từng tab trong port
            if status_summary['total_tabs'] > 0:
                print(f"    📋 Tabs detail:")
                for tab_id, tab_state in sorted(port_state.tabs.items()):
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
                    
                    print(f"      {status_icon} Tab {tab_id} ({tab_state.container_name})")
                    print(f"         Status: {tab_state.status.value} | Last used: {time_str}")
                    print(f"         {can_accept} | Errors: {tab_state.error_count}")
                    if tab_state.current_request_id:
                        print(f"         Current request: {tab_state.current_request_id}")
        
        # 2. Lấy tab rảnh với cơ chế thông minh
        print("\n[API] 🎯 SELECTING FREE TAB...")
        tab_info = await port_manager.get_free_tab()
        
        if not tab_info:
            busy_count = port_manager.get_busy_count()
            free_count = port_manager.get_total_free_tabs()
            connected_count = port_manager.get_connected_count()
            
            print("\n[API] ❌ NO FREE TAB AVAILABLE!")
            print(f"  Reason: connected={connected_count}, free={free_count}, busy={busy_count}")
            print("="*80 + "\n")
            
            if connected_count == 0:
                raise HTTPException(
                    status_code=503,
                    detail="No ZenTab connections available. Please open ZenTab extension first."
                )
            elif free_count == 0:
                raise HTTPException(
                    status_code=503,
                    detail=f"No free tabs available. {busy_count} tabs are busy. Please try again in a few seconds."
                )
            else:
                # Có tab free nhưng không đủ điều kiện (chưa đủ thời gian chờ)
                raise HTTPException(
                    status_code=503,
                    detail="Tabs are cooling down after previous requests. Please try again in 2-3 seconds."
                )
        
        port, tab_id, port_state, tab_state = tab_info
        
        # 🆕 LOG: Thông tin tab được chọn
        print(f"\n[API] ✅ SELECTED TAB:")
        print(f"  ├─ Port: {port}")
        print(f"  ├─ Tab ID: {tab_id}")
        print(f"  ├─ Container: {tab_state.container_name}")
        print(f"  ├─ Title: {tab_state.title}")
        print(f"  ├─ Status: {tab_state.status.value}")
        print(f"  ├─ Error count: {tab_state.error_count}")
        print(f"  └─ Last used: {time.time() - tab_state.last_used:.1f}s ago")
        
        # 3. Tạo request ID và gửi prompt
        request_id = f"api-{uuid.uuid4().hex[:16]}"
        
        # Extract user message (lấy message cuối cùng từ user)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")
        
        prompt = user_messages[-1].content
        
        print(f"[API] 🎯 Selected tab {tab_id} ({tab_state.container_name}) on port {port}")
        
        # 4. Gửi request tới ZenTab qua WebSocket
        tab_state.mark_busy(request_id)
        port_manager.request_to_tab[request_id] = (port, tab_id)
        
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "prompt": prompt,
            "requestId": request_id
        }
        
        try:
            await port_state.websocket.send(json.dumps(ws_message))
            print(f"\n[API] 📤 PROMPT SENT:")
            print(f"  ├─ Request ID: {request_id}")
            print(f"  ├─ Target: Port {port}, Tab {tab_id}")
            print(f"  └─ Prompt length: {len(prompt)} chars")
            print(f"\n[API] ⏳ Waiting for response (timeout: {REQUEST_TIMEOUT}s)...")
        except Exception as e:
            # Gửi thất bại: đánh dấu tab rảnh lại
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
            # Lỗi khác: đánh dấu tab rảnh
            if request_id in port_manager.request_to_tab:
                port, tab_id = port_manager.request_to_tab[request_id]
                if port in port_manager.ports and tab_id in port_manager.ports[port].tabs:
                    port_manager.ports[port].tabs[tab_id].mark_free()
                port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=str(e))
    
    # Register router
    app.include_router(router)