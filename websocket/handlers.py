import json
import time
import asyncio
from websockets.server import WebSocketServerProtocol
import websockets

async def handle_websocket_connection(websocket: WebSocketServerProtocol, port_manager):
    await port_manager.update_websocket(websocket)
    ping_task = None
    
    try:
        async def send_ping():
            while port_manager.websocket == websocket:
                try:
                    await websocket.ping()
                    await asyncio.sleep(30)
                except Exception:
                    break
        
        ping_task = asyncio.create_task(send_ping())
        
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_websocket_message(data, port_manager)
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception:
        pass
    finally:
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
    VALIDATE_TIMESTAMP_TYPES = ["getAvailableTabs", "focusedTabsUpdate", "promptResponse"]
    
    if msg_type in VALIDATE_TIMESTAMP_TYPES:
        message_timestamp = data.get("timestamp", 0)
        if message_timestamp > 0:
            message_timestamp_seconds = message_timestamp / 1000.0
            current_time = time.time()
            message_age = current_time - message_timestamp_seconds
            
            if message_age > 60:
                return
            
            if message_age < -5:
                return
    
    if msg_type == "getAvailableTabs":
        return
    
    elif msg_type == "availableTabs":
        request_id = data.get("requestId")
        tabs = data.get("tabs", [])
        
        # Check if future exists and not done
        if request_id not in port_manager.response_futures:
            return
        
        future = port_manager.response_futures.get(request_id)
        if future.done():
            return
        
        # Validate tabs data structure
        if not isinstance(tabs, list):
            tabs = []
        
        # Resolve future cho request này
        port_manager.handle_available_tabs_response(request_id, tabs)
    
    elif msg_type == "focusedTabsUpdate":
        return
        
    elif msg_type == "promptResponse":
        request_id = data.get("requestId")
        success = data.get("success", False)
        tab_id = data.get("tabId")
        error_type = data.get("errorType", "")
        response_text = data.get("response", "")
        message_timestamp = data.get("timestamp", 0)
        
        message_timestamp_seconds = message_timestamp / 1000.0 if message_timestamp > 0 else 0
        message_age = time.time() - message_timestamp_seconds if message_timestamp > 0 else 0
        message_key = f"{message_timestamp}_{request_id}"
        
        in_response_futures = request_id in port_manager.response_futures
        in_progress = port_manager.is_request_in_progress(request_id)
        already_processed = port_manager.is_request_processed(request_id)
        message_too_old = message_age > 30.0
        in_request_to_tab = request_id in port_manager.request_to_tab
        expected_tab_id = port_manager.request_to_tab.get(request_id) if in_request_to_tab else None
        already_forwarded = message_key in port_manager.forwarded_messages
        
        future_done = False
        if in_response_futures:
            future = port_manager.response_futures.get(request_id)
            future_done = future.done() if future else False
        
        should_process = (
            in_response_futures and 
            not in_progress and 
            not already_processed and 
            not message_too_old and
            not already_forwarded and
            not future_done
        )
        
        if not should_process:
            return
        
        port_manager.mark_request_in_progress(request_id)
        
        current_time = time.time()
        port_manager.forwarded_messages[message_key] = current_time
        
        if not request_id or tab_id is None:
            port_manager.mark_request_completed(request_id)
            return
        
        if request_id not in port_manager.request_to_tab:
            expected_tab_id = None
        else:
            expected_tab_id = port_manager.request_to_tab[request_id]
        
        if expected_tab_id is not None and expected_tab_id != tab_id:
            port_manager.mark_request_completed(request_id)
            return
        
        if not success:
            error_msg = data.get("error", "Unknown error")
            port_manager.resolve_response(request_id, {"error": error_msg})
            port_manager.mark_request_processed(request_id)
            port_manager.mark_request_completed(request_id)
            return
        
        response_text = data.get("response", "")
        
        if isinstance(response_text, bytes):
            try:
                response_text = response_text.decode('utf-8')
            except Exception:
                pass
        
        try:
            if isinstance(response_text, dict):
                response_data = response_text
            elif not response_text:
                raise ValueError("Empty response received")
            elif isinstance(response_text, str):
                # 🆕 FIX: Parse JSON ONCE và decode escaped sequences
                try:
                    # Single parse - ZenTab đã stringify 1 lần
                    response_data = json.loads(response_text)
                    
                    # 🔥 CRITICAL: Decode escaped newlines trong content field
                    if isinstance(response_data, dict) and 'choices' in response_data:
                        for choice in response_data.get('choices', []):
                            # Check cả message và delta
                            for key in ['message', 'delta']:
                                if key in choice and 'content' in choice[key]:
                                    raw_content = choice[key]['content']
                                    if isinstance(raw_content, str) and '\\n' in raw_content:
                                        # Decode escaped sequences
                                        decoded_content = raw_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
                                        choice[key]['content'] = decoded_content
                    
                except json.JSONDecodeError:
                    # Fallback: nếu parse fail, dùng response_parser
                    from core.response_parser import parse_deepseek_response
                    response_data = parse_deepseek_response(response_text)
            else:
                response_data = json.loads(str(response_text))
            
        except (json.JSONDecodeError, TypeError):
            from core.response_parser import parse_deepseek_response
            response_data = parse_deepseek_response(response_text)
        
        if request_id not in port_manager.response_futures:
            port_manager.mark_request_completed(request_id)
            return
        
        port_manager.resolve_response(request_id, response_data)
        
        port_manager.mark_request_processed(request_id)
        port_manager.mark_request_completed(request_id)
        
        asyncio.create_task(port_manager.schedule_request_cleanup(request_id, delay=10.0))