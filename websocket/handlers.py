"""
WebSocket message handlers - Single connection version
"""
import json
import time
import asyncio  # 🔧 THÊM: Import asyncio
from websockets.server import WebSocketServerProtocol
import websockets

from core.response_parser import parse_deepseek_response
from models import TabState

async def handle_websocket_connection(websocket: WebSocketServerProtocol, port_manager):
    await port_manager.update_websocket(websocket)
    ping_task = None
    
    try:
        async def send_ping():
            while port_manager.websocket == websocket:
                try:
                    await websocket.ping()
                    await asyncio.sleep(30)
                except Exception as e:
                    break
        
        # Start ping task
        ping_task = asyncio.create_task(send_ping())
        
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_websocket_message(data, port_manager)
            except json.JSONDecodeError:
                print(f"[WS:{port_manager.port}] ❌ Invalid JSON: {message}")
            except Exception as e:
                print(f"[WS:{portManager.port}] ❌ Error handling message: {e}")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[WS:{port_manager.port}] 🔌 ZenTab disconnected: {e.code} - {e.reason}")
    except Exception as e:
        print(f"[WS:{port_manager.port}] ❌ Unexpected error: {e}")
    finally:
        # Cancel ping task
        if ping_task:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass
        
        if port_manager.websocket == websocket:
            port_manager.websocket = None

async def handle_websocket_message(data: dict, port_manager):
    msg_type = data.get("type")
    VALIDATE_TIMESTAMP_TYPES = ["getAvailableTabs", "focusedTabsUpdate"]
    
    if msg_type in VALIDATE_TIMESTAMP_TYPES:
        message_timestamp = data.get("timestamp", 0)
        current_time = time.time()
        if message_timestamp > 0 and current_time - message_timestamp > 30:  # 30 seconds threshold
            return
    
    if msg_type == "getAvailableTabs":
        return
        request_id = data.get("requestId")
        
        request_msg = {
            "type": "getAvailableTabs",
            "requestId": request_id,
            "timestamp": time.time()
        }
        
        try:
            await port_manager.websocket.send(json.dumps(request_msg))
        except Exception as e:
            print(f"[WS:{port_manager.port}] ❌ Failed to forward getAvailableTabs: {e}")
    
    elif msg_type == "availableTabs":
        request_id = data.get("requestId")
        tabs = data.get("tabs", [])
        port_manager.handle_available_tabs_response(request_id, tabs)
    
    elif msg_type == "focusedTabsUpdate":
        return
        
    elif msg_type == "promptResponse":
        # ZenTab trả response từ DeepSeek
        request_id = data.get("requestId")
        success = data.get("success", False)
        tab_id = data.get("tabId")
        error_type = data.get("errorType", "")
        
        if not request_id or tab_id is None:
            return
        
        if request_id not in port_manager.request_to_tab:
            return
        
        expected_tab_id = port_manager.request_to_tab[request_id]
        
        if expected_tab_id != tab_id:
            return
        
        # Lấy tab state từ temp_tab_states
        tab_state = port_manager.get_temp_tab_state(tab_id)
        if not tab_state:
            port_manager.resolve_response(request_id, {"error": "Tab not found"})
            return
        
        # Xử lý lỗi
        if not success:
            error_msg = data.get("error", "Unknown error")            
            # Cleanup tab state tạm thời
            port_manager.cleanup_temp_tab_state(tab_id)
            
            # Resolve error
            port_manager.resolve_response(request_id, {"error": error_msg})
            return
        
        response_text = data.get("response", "")
        
        # Parse response
        parsed_response = parse_deepseek_response(response_text)
        
        # Cleanup tab state tạm thời
        port_manager.cleanup_temp_tab_state(tab_id)
        
        # Resolve response
        port_manager.resolve_response(request_id, parsed_response)
        
    elif msg_type == "promptResponse":
        # ZenTab trả response từ DeepSeek
        request_id = data.get("requestId")
        success = data.get("success", False)
        tab_id = data.get("tabId")
        error_type = data.get("errorType", "")
        
        if not request_id or tab_id is None:
            return
        
        if request_id not in port_manager.request_to_tab:
            return
        
        expected_tab_id = port_manager.request_to_tab[request_id]
        
        if expected_tab_id != tab_id:
            return
        
        # Lấy tab state từ global pool
        tab_state = port_manager.global_tab_pool.get(tab_id)
        if not tab_state:
            port_manager.resolve_response(request_id, {"error": "Tab not found"})
            return
        
        # Xử lý lỗi
        if not success:
            error_msg = data.get("error", "Unknown error")
            
            # Đánh dấu tab error (hoặc xóa nếu không tồn tại)
            if error_type in ["SEND_FAILED", "VALIDATION_FAILED"]:
                tab_state.mark_not_found()
            else:
                tab_state.mark_error()
            
            # Resolve error
            port_manager.resolve_response(request_id, {"error": error_msg})
            await port_manager.broadcast_status_update()
            return
        
        response_text = data.get("response", "")
        
        # Parse response
        parsed_response = parse_deepseek_response(response_text)
        
        # Đánh dấu tab rảnh
        tab_state.mark_free()
        
        # Resolve response
        port_manager.resolve_response(request_id, parsed_response)
        
        # Broadcast status update
        await port_manager.broadcast_status_update()