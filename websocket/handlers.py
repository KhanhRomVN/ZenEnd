"""
WebSocket message handlers
"""
import json
from websockets.server import WebSocketServerProtocol
import websockets

from core.response_parser import parse_deepseek_response


async def handle_websocket_connection(websocket: WebSocketServerProtocol, port: int, port_manager):
    """Xử lý WebSocket connection từ ZenTab"""
    port_state = port_manager.ports[port]
    port_state.websocket = websocket
    
    print(f"[WS:{port}] ✅ ZenTab connected")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_websocket_message(data, port, port_manager)
            except json.JSONDecodeError:
                print(f"[WS:{port}] ❌ Invalid JSON: {message}")
            except Exception as e:
                print(f"[WS:{port}] ❌ Error handling message: {e}")
    except websockets.exceptions.ConnectionClosed:
        print(f"[WS:{port}] 🔌 ZenTab disconnected")
    finally:
        port_state.websocket = None
        # Reset tất cả tabs trong port này khi mất kết nối
        port_state.tabs = {}


async def handle_websocket_message(data: dict, port: int, port_manager):
    """Xử lý message từ ZenTab"""
    msg_type = data.get("type")
    port_state = port_manager.ports[port]
    
    if msg_type == "focusedTabsUpdate":
        # ZenTab gửi thông tin tabs - CẬP NHẬT danh sách tabs
        focused_tabs = data.get('data', [])
        port_state.update_tabs(focused_tabs)
        
        status_summary = port_state.get_tab_status_summary()
        print(f"[WS:{port}] 📋 Focused tabs update: {status_summary}")
        
    elif msg_type == "promptResponse":
        # ZenTab trả response từ DeepSeek
        request_id = data.get("requestId")
        success = data.get("success", False)
        tab_id = data.get("tabId")
        error_type = data.get("errorType", "")
        
        if not request_id or tab_id is None:
            print(f"[WS:{port}] ❌ Missing requestId or tabId in response")
            return
        
        # 🔧 FIX: Nếu error là SEND_FAILED, resolve ngay lập tức
        if not success and error_type == "SEND_FAILED":
            error_msg = data.get("error", "Unknown error")
            print(f"[WS:{port}] ❌ Send failed for {request_id}: {error_msg}")
            
            # Resolve response để unblock HTTP request
            port_manager.resolve_response(request_id, {"error": error_msg})
            
            # 🔧 CRITICAL: Remove invalid tab khỏi port_state.tabs
            if tab_id in port_state.tabs:
                del port_state.tabs[tab_id]
                print(f"[WS:{port}] 🗑️ Removed invalid tab {tab_id} from port state")
            
            return
        
        # 🔧 FIX: Handle VALIDATION_FAILED
        if not success and error_type == "VALIDATION_FAILED":
            error_msg = data.get("error", "Unknown error")
            print(f"[WS:{port}] ❌ Validation failed for {request_id}: {error_msg}")
            
            # Resolve response để unblock HTTP request
            port_manager.resolve_response(request_id, {"error": error_msg})
            
            # 🔧 CRITICAL: Remove invalid tab khỏi port_state.tabs
            if tab_id in port_state.tabs:
                del port_state.tabs[tab_id]
                print(f"[WS:{port}] 🗑️ Removed invalid tab {tab_id} due to validation failure")
            
            return

        # Tìm tab tương ứng
        if tab_id not in port_state.tabs:
            print(f"[WS:{port}] ❌ Tab {tab_id} not found for response")
            # Vẫn resolve để unblock request
            error = data.get("error", "Tab not found")
            port_manager.resolve_response(request_id, {"error": error})
            return
            
        tab_state = port_state.tabs[tab_id]
        
        if success:
            response_text = data.get("response", "")
            print(f"[WS:{port}] ✅ Response received for {request_id} from tab {tab_id}")
            
            # Parse response từ DeepSeek format
            parsed_response = parse_deepseek_response(response_text)
            
            # Resolve future để trả về HTTP response
            port_manager.resolve_response(request_id, parsed_response)
            
            # Đánh dấu tab rảnh thành công
            tab_state.mark_free()
            
        else:
            error = data.get("error", "Unknown error")
            print(f"[WS:{port}] ❌ Error for {request_id} from tab {tab_id}: {error}")
            
            # Xử lý lỗi dựa trên loại lỗi
            if "Invalid tab ID" in error or "Tab not found" in error:
                tab_state.mark_not_found()
                print(f"[WS:{port}] 🗑️ Marked tab {tab_id} as NOT_FOUND")
            else:
                tab_state.mark_error()
                print(f"[WS:{port}] ⚠️ Marked tab {tab_id} as ERROR (count: {tab_state.error_count})")
            
            port_manager.resolve_response(request_id, {"error": error})