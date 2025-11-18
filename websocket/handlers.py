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
    """Xử lý WebSocket connection từ ZenTab"""
    print(f"[WS:{port_manager.port}] 🔌 New connection attempt from ZenTab")
    print(f"[WS:{port_manager.port}]   - PortManager instance ID: {id(port_manager)}")
    print(f"[WS:{port_manager.port}]   - WebSocket object: {websocket}")
    print(f"[WS:{port_manager.port}]   - Is open: {websocket.open}")
    
    # 🆕 FIX: Cập nhật websocket trước khi xử lý
    await port_manager.update_websocket(websocket)
    
    print(f"[WS:{port_manager.port}] ✅ ZenTab connected")
    print(f"[WS:{port_manager.port}] 🔄 PortManager.websocket updated successfully")
    print(f"[WS:{port_manager.port}]   - port_manager.websocket is None: {port_manager.websocket is None}")
    print(f"[WS:{port_manager.port}]   - port_manager.websocket is open: {port_manager.websocket.open if port_manager.websocket else 'N/A'}")
    
    # 🆕 XÓA: Không gửi broadcast tự động nữa
    # Chỉ kết nối đơn thuần, tabs sẽ được request khi cần
    
    # 🆕 THÊM: Biến để track ping task
    ping_task = None
    
    # 🆕 THÊM: Biến để track ping task
    ping_task = None
    
    try:
        # 🆕 THÊM: Send ping để keep-alive connection
        async def send_ping():
            while port_manager.websocket == websocket:
                try:
                    await websocket.ping()
                    await asyncio.sleep(30)  # Ping every 30s
                except Exception as e:
                    print(f"[WS:{port_manager.port}] ⚠️ Ping failed: {e}")
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
        print(f"[WS:{port_manager.port}] 🔌 Connection closing...")
        print(f"[WS:{port_manager.port}]   - port_manager.websocket before clear: {port_manager.websocket}")
        print(f"[WS:{port_manager.port}]   - Is same as current connection: {port_manager.websocket == websocket}")
        
        if port_manager.websocket == websocket:
            print(f"[WS:{port_manager.port}] 🔌 Connection closing...")
            print(f"[WS:{port_manager.port}] 📊 Preserving {len(port_manager.global_tab_pool)} tabs in pool")
            port_manager.websocket = None
            print(f"[WS:{port_manager.port}] ✅ WebSocket cleared, tabs preserved")
            print(f"[WS:{port_manager.port}]   - port_manager.websocket after clear: {port_manager.websocket}")
        else:
            print(f"[WS:{port_manager.port}] ⏩ Not clearing websocket (not current connection)")

async def handle_websocket_message(data: dict, port_manager):
    msg_type = data.get("type")
    
    print(f"[WS:{port_manager.port}] 📥 Received message from extension: type={msg_type}")
    
    # 🔧 FIX: Chỉ validate timestamp cho một số message types nhất định
    # KHÔNG validate cho promptResponse vì có thể bị delay lâu do AI processing
    VALIDATE_TIMESTAMP_TYPES = ["getAvailableTabs", "focusedTabsUpdate"]
    
    if msg_type in VALIDATE_TIMESTAMP_TYPES:
        message_timestamp = data.get("timestamp", 0)
        current_time = time.time()
        if message_timestamp > 0 and current_time - message_timestamp > 30:  # 30 seconds threshold
            print(f"[WS:{port_manager.port}] ⏩ Ignoring old message (type: {msg_type}, age: {current_time - message_timestamp:.1f}s)")
            return
    
    # 🆕 THÊM: Xử lý yêu cầu danh sách tabs từ backend
    if msg_type == "getAvailableTabs":
        print(f"[WS:{port_manager.port}] ⚠️ ERROR: Received getAvailableTabs FROM extension, but this should be sent TO extension!")
        print(f"[WS:{port_manager.port}] This indicates a logic error - Backend should send this, not receive it")
        return
        request_id = data.get("requestId")
        print(f"[WS:{port_manager.port}] 📡 Received getAvailableTabs request: {request_id}")
        
        # Gửi message tới extension để lấy danh sách tabs
        # Extension sẽ trả lời qua message "availableTabs"
        request_msg = {
            "type": "getAvailableTabs",
            "requestId": request_id,
            "timestamp": time.time()
        }
        
        try:
            await port_manager.websocket.send(json.dumps(request_msg))
            print(f"[WS:{port_manager.port}] 📤 Forwarded getAvailableTabs to extension")
        except Exception as e:
            print(f"[WS:{port_manager.port}] ❌ Failed to forward getAvailableTabs: {e}")
    
    # 🆕 THÊM: Xử lý response danh sách tabs từ extension
    elif msg_type == "availableTabs":
        request_id = data.get("requestId")
        tabs = data.get("tabs", [])
        
        print(f"[WS:{port_manager.port}] 📋 Received availableTabs response:")
        print(f"[WS:{port_manager.port}]   - Request ID: {request_id}")
        print(f"[WS:{port_manager.port}]   - Total tabs: {len(tabs)}")
        print(f"[WS:{port_manager.port}]   - Tabs: {tabs}")
        
        port_manager.handle_available_tabs_response(request_id, tabs)
    
    # Các message type khác giữ nguyên
    elif msg_type == "focusedTabsUpdate":
        # 🔧 FIX: Không xử lý focusedTabsUpdate tự động nữa
        print(f"[WS:{port_manager.port}] ⏩ Skipping focusedTabsUpdate (using on-demand tabs)")
        return
        
    elif msg_type == "promptResponse":
        # ZenTab trả response từ DeepSeek
        request_id = data.get("requestId")
        success = data.get("success", False)
        tab_id = data.get("tabId")
        error_type = data.get("errorType", "")
        
        print(f"[WS:{port_manager.port}] 📥 Received promptResponse:")
        print(f"[WS:{port_manager.port}]   - Request ID: {request_id}")
        print(f"[WS:{port_manager.port}]   - Tab ID: {tab_id}")
        print(f"[WS:{port_manager.port}]   - Success: {success}")
        print(f"[WS:{port_manager.port}]   - Message timestamp: {data.get('timestamp', 'N/A')}")
        
        if not request_id or tab_id is None:
            print(f"[WS:{port_manager.port}] ❌ Missing requestId or tabId in response")
            return
        
        # ✅ Kiểm tra request có tồn tại không
        if request_id not in port_manager.request_to_tab:
            print(f"[WS:{port_manager.port}] ⚠️ Unknown request {request_id}")
            print(f"[WS:{port_manager.port}] 📋 Current tracked requests: {list(port_manager.request_to_tab.keys())}")
            return
        
        expected_tab_id = port_manager.request_to_tab[request_id]
        
        # ✅ Kiểm tra tab có đúng không
        if expected_tab_id != tab_id:
            print(f"[WS:{port_manager.port}] ❌ Tab mismatch: expected {expected_tab_id}, got {tab_id}")
            return
        
        # Lấy tab state từ temp_tab_states
        tab_state = port_manager.get_temp_tab_state(tab_id)
        if not tab_state:
            print(f"[WS:{port_manager.port}] ❌ Tab {tab_id} not in temp states")
            port_manager.resolve_response(request_id, {"error": "Tab not found"})
            return
        
        # Xử lý lỗi
        if not success:
            error_msg = data.get("error", "Unknown error")
            print(f"[WS:{port_manager.port}] ❌ Error for {request_id}: {error_msg}")
            
            # Cleanup tab state tạm thời
            port_manager.cleanup_temp_tab_state(tab_id)
            
            # Resolve error
            port_manager.resolve_response(request_id, {"error": error_msg})
            return
        
        # ✅ SUCCESS
        response_text = data.get("response", "")
        print(f"[WS:{port_manager.port}] ✅ Response received for {request_id} from tab {tab_id}")
        
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
        
        print(f"[WS:{port_manager.port}] 📥 Received promptResponse:")
        print(f"[WS:{port_manager.port}]   - Request ID: {request_id}")
        print(f"[WS:{port_manager.port}]   - Tab ID: {tab_id}")
        print(f"[WS:{port_manager.port}]   - Success: {success}")
        print(f"[WS:{port_manager.port}]   - Message timestamp: {data.get('timestamp', 'N/A')}")
        
        if not request_id or tab_id is None:
            print(f"[WS:{port_manager.port}] ❌ Missing requestId or tabId in response")
            return
        
        # ✅ Kiểm tra request có tồn tại không
        if request_id not in port_manager.request_to_tab:
            print(f"[WS:{port_manager.port}] ⚠️ Unknown request {request_id}")
            print(f"[WS:{port_manager.port}] 📋 Current tracked requests: {list(port_manager.request_to_tab.keys())}")
            return
        
        expected_tab_id = port_manager.request_to_tab[request_id]
        
        # ✅ Kiểm tra tab có đúng không
        if expected_tab_id != tab_id:
            print(f"[WS:{port_manager.port}] ❌ Tab mismatch: expected {expected_tab_id}, got {tab_id}")
            return
        
        # Lấy tab state từ global pool
        tab_state = port_manager.global_tab_pool.get(tab_id)
        if not tab_state:
            print(f"[WS:{port_manager.port}] ❌ Tab {tab_id} not in global pool")
            port_manager.resolve_response(request_id, {"error": "Tab not found"})
            return
        
        # Xử lý lỗi
        if not success:
            error_msg = data.get("error", "Unknown error")
            print(f"[WS:{port_manager.port}] ❌ Error for {request_id}: {error_msg}")
            
            # Đánh dấu tab error (hoặc xóa nếu không tồn tại)
            if error_type in ["SEND_FAILED", "VALIDATION_FAILED"]:
                tab_state.mark_not_found()
                print(f"[WS:{port_manager.port}] 🗑️ Tab {tab_id} marked as NOT_FOUND")
            else:
                tab_state.mark_error()
                print(f"[WS:{port_manager.port}] ⚠️ Tab {tab_id} marked as ERROR (count: {tab_state.error_count})")
            
            # Resolve error
            port_manager.resolve_response(request_id, {"error": error_msg})
            await port_manager.broadcast_status_update()
            return
        
        # ✅ SUCCESS
        response_text = data.get("response", "")
        print(f"[WS:{port_manager.port}] ✅ Response received for {request_id} from tab {tab_id}")
        
        # Parse response
        parsed_response = parse_deepseek_response(response_text)
        
        # Đánh dấu tab rảnh
        tab_state.mark_free()
        
        # Resolve response
        port_manager.resolve_response(request_id, parsed_response)
        
        # Broadcast status update
        await port_manager.broadcast_status_update()