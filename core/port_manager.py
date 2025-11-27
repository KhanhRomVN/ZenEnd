import uuid
import json
import time
import asyncio
from typing import Dict, Optional, Tuple
from fastapi import HTTPException
from core.logger import error_response


class PortManager:
    _instance = None
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._lock = asyncio.Lock()
            cls._instance._initialized = False
        
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.websocket: Optional[object] = None
        
        self.response_futures: Dict[str, asyncio.Future] = {}
        self.request_to_tab: Dict[str, int] = {}
        self.processed_requests: Dict[str, float] = {}
        self.duplicate_count: Dict[str, int] = {}
        self.requests_in_progress: set[str] = set()
        
        self.lock = asyncio.Lock()
        self.connection_time = 0
        self.connection_start_time = 0
        
        self._initialized = True
        self._cleanup_task = None
        
        self.forwarded_messages: Dict[str, float] = {}
        self.message_processing_log: Dict[str, list] = {}
    
    async def reconnect_websocket(self, max_retries: int = 3):        
        # Simply check if we have a websocket object
        if self.websocket:
            return True
        else:
            return False

    def mark_request_in_progress(self, request_id: str):
        self.requests_in_progress.add(request_id)
        
        if request_id not in self.message_processing_log:
            self.message_processing_log[request_id] = []
        self.message_processing_log[request_id].append(f"IN_PROGRESS at {time.time()}")
        
        asyncio.create_task(self._auto_cleanup_request(request_id))

    async def _auto_cleanup_request(self, request_id: str):
        await asyncio.sleep(30)
        if request_id in self.requests_in_progress:
            self.requests_in_progress.discard(request_id)
            
            if request_id in self.request_to_tab:
                self.request_to_tab.pop(request_id, None)

    def mark_request_completed(self, request_id: str):
        if request_id in self.requests_in_progress:
            self.requests_in_progress.discard(request_id)
            
            if request_id not in self.message_processing_log:
                self.message_processing_log[request_id] = []
            self.message_processing_log[request_id].append(f"COMPLETED at {time.time()}")

    def is_request_in_progress(self, request_id: str) -> bool:
        return request_id in self.requests_in_progress
    
    async def start_cleanup_loop(self):
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def is_duplicate_request(self, request_id: str) -> bool:
        if request_id in self.processed_requests:
            request_time = self.processed_requests[request_id]
            time_since_processed = time.time() - request_time
            
            if time_since_processed < 30.0:
                dup_count = self.duplicate_count.get(request_id, 0) + 1
                self.duplicate_count[request_id] = dup_count
                return True
            else:
                self.processed_requests.pop(request_id, None)
                self.duplicate_count.pop(request_id, None)
                return False
        else:
            return False

    def is_request_processed(self, request_id: str) -> bool:
        return self.is_duplicate_request(request_id)

    def mark_request_processed(self, request_id: str):
        current_time = time.time()
        self.processed_requests[request_id] = current_time
        
        if request_id not in self.message_processing_log:
            self.message_processing_log[request_id] = []
        self.message_processing_log[request_id].append(f"PROCESSED at {current_time}")

    async def cleanup_old_requests(self):
        current_time = time.time()
        keys_to_remove = []
        
        for req_id, timestamp in self.processed_requests.items():
            if current_time - timestamp > 60:
                keys_to_remove.append(req_id)
        
        for req_id in keys_to_remove:
            self.processed_requests.pop(req_id, None)
            self.duplicate_count.pop(req_id, None)
            
            if req_id in self.message_processing_log:
                self.message_processing_log.pop(req_id, None)
    
    async def cleanup_forwarded_messages(self):
        current_time = time.time()
        keys_to_remove = []
        
        for msg_key, timestamp in self.forwarded_messages.items():
            if current_time - timestamp > 300:
                keys_to_remove.append(msg_key)
        
        for msg_key in keys_to_remove:
            self.forwarded_messages.pop(msg_key, None)
    
    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(300)
            await self.cleanup_old_requests()
            await self.cleanup_forwarded_messages()

    def get_connection_status(self) -> dict:        
        websocket_open = False
        websocket_connected = False
        
        if self.websocket:
            websocket_connected = True
            try:
                # 🔥 CRITICAL FIX: FastAPI WebSocket check
                # FastAPI WebSocket uses client_state and application_state
                if hasattr(self.websocket, 'client_state'):
                    # FastAPI WebSocket
                    from starlette.websockets import WebSocketState
                    websocket_open = self.websocket.client_state == WebSocketState.CONNECTED
                    
                elif hasattr(self.websocket, 'closed'):
                    # Standard WebSocket
                    websocket_open = not self.websocket.closed
                elif hasattr(self.websocket, 'open'):
                    websocket_open = self.websocket.open
                elif hasattr(self.websocket, 'state'):
                    # websockets library
                    from websockets.protocol import State
                    websocket_open = self.websocket.state == State.OPEN
                else:
                    # Fallback: assume open if we have the object
                    websocket_open = True
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                websocket_open = False
                
        status = {
            "websocket_connected": websocket_connected,
            "websocket_open": websocket_open,
            "connection_age": time.time() - self.connection_start_time if self.connection_start_time > 0 else 0
        }
        
        return status
    
    async def update_websocket(self, websocket):
        async with self.lock:
            self.websocket = websocket
            self.connection_time = time.time()
            self.connection_start_time = time.time()
    
    async def broadcast_status_update(self):
        if self.websocket:
            try:
                status_data = {
                    "type": "statusUpdate",
                    "data": self.get_detailed_status(),
                    "timestamp": time.time()
                }
                await self.websocket.send(json.dumps(status_data))
            except Exception:
                pass
    
    def resolve_response(self, request_id: str, response: dict):
        future = self.response_futures.get(request_id)
        
        if future and not future.done():
            try:
                future.set_result(response)
            except Exception:
                pass
    
    async def wait_for_response(self, request_id: str, timeout: float = 180.0) -> dict:
        """
        Đợi response từ ZenTab extension với timeout
        
        Args:
            request_id: ID của request cần đợi response
            timeout: Thời gian tối đa chờ (giây)
            
        Returns:
            dict: Response data từ ZenTab hoặc dict chứa error field
        """
        # Tạo future để chờ response
        future = asyncio.Future()
        self.response_futures[request_id] = future
        
        try:
            # Đợi response với timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            
            # 🔥 FIX: KHÔNG raise HTTPException - chỉ return dict với error
            # Kiểm tra response có lỗi không
            if "error" in response:
                error_msg = response.get("error", "Unknown error")
                
                # Classify error type
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    error_type = "COOLING_DOWN"
                    status_hint = 503
                else:
                    error_type = "TAB_ERROR"
                    status_hint = 500
                
                # Return error dict thay vì raise
                return {
                    "error": error_msg,
                    "error_type": error_type,
                    "status_hint": status_hint,
                    "request_id": request_id
                }
            
            # Return success response
            return response
            
        except asyncio.TimeoutError:
            # Cleanup khi timeout
            self.response_futures.pop(request_id, None)
            self.request_to_tab.pop(request_id, None)
            
            # Return timeout error dict
            return {
                "error": f"Request đã timeout sau {timeout} giây. DeepSeek mất quá nhiều thời gian để phản hồi.",
                "error_type": "TIMEOUT",
                "timeout_seconds": timeout,
                "status_hint": 504,
                "request_id": request_id
            }
            
        except Exception as e:
            # Cleanup khi có lỗi
            self.response_futures.pop(request_id, None)
            self.request_to_tab.pop(request_id, None)
            
            # Log exception với traceback
            import traceback
            tb = traceback.format_exc()
            
            # 🔥 FIX: Đảm bảo error message KHÔNG BAO GIỜ rỗng
            error_message = str(e) if str(e) else f"Unknown exception: {type(e).__name__}"
            
            # Return exception error dict
            return {
                "error": f"Exception trong wait_for_response: {error_message}",
                "error_type": "EXCEPTION",
                "exception_class": type(e).__name__,
                "traceback_preview": tb[:500],  # Truncate for safety
                "status_hint": 500,
                "request_id": request_id
            }
            
        finally:
            # Luôn cleanup future sau khi xong
            self.response_futures.pop(request_id, None)

    async def cleanup_pending_messages(self):
        try:
            cleanup_message = {
                "type": "cleanupMessages",
                "timestamp": time.time(),
                "force": True
            }
                        
            if self.websocket:
                try:
                    await self.websocket.send(json.dumps(cleanup_message))
                except Exception:
                    pass
            
        except Exception:
            pass

    async def request_fresh_tabs(self, timeout: float = 10.0) -> list:
        """
        Request danh sách tabs rảnh từ ZenTab extension
        🔥 FIX: Chỉ trả về tabs có canAccept=true và status=free
        """
        if not self.websocket:
            return []
        
        try:
            # Check websocket state properly
            if hasattr(self.websocket, 'client_state'):
                # FastAPI WebSocket
                from starlette.websockets import WebSocketState
                if self.websocket.client_state != WebSocketState.CONNECTED:
                    return []
            elif hasattr(self.websocket, 'state'):
                from websockets.protocol import State
                if self.websocket.state != State.OPEN:
                    return []
            elif hasattr(self.websocket, 'closed'):
                if self.websocket.closed:
                    return []
        except Exception:
            return []

        request_id = f"tabs_req_{uuid.uuid4().hex[:8]}"
        
        future = asyncio.Future()
        self.response_futures[request_id] = future

        try:
            request_msg = {
                "type": "getAvailableTabs",
                "requestId": request_id,
                "timestamp": int(time.time() * 1000),
                "urgent": True
            }
            
            await self.websocket.send_text(json.dumps(request_msg))
            
            response = await asyncio.wait_for(future, timeout=timeout)
            tabs = response.get('tabs', [])
            
            # 🔥 CRITICAL FIX: Chỉ trả tabs THỰC SỰ rảnh (canAccept=true và status=free)
            free_tabs = [
                tab for tab in tabs 
                if tab.get('canAccept', False) and tab.get('status') == 'free'
            ]
            
            return free_tabs
            
        except asyncio.TimeoutError:
            return []
        except Exception:
            return []
        finally:
            self.response_futures.pop(request_id, None)

    async def request_tabs_by_folder(self, folder_path: str, timeout: float = 10.0) -> list:
        """
        Request danh sách tabs có folder_path khớp từ ZenTab.
        🔥 FIX: Chỉ trả về tabs có canAccept=true và status=free
        """
        if not self.websocket:
            return []
        
        try:
            # Check websocket state properly
            if hasattr(self.websocket, 'client_state'):
                # FastAPI WebSocket
                from starlette.websockets import WebSocketState
                if self.websocket.client_state != WebSocketState.CONNECTED:
                    return []
            elif hasattr(self.websocket, 'state'):
                from websockets.protocol import State
                if self.websocket.state != State.OPEN:
                    return []
            elif hasattr(self.websocket, 'closed'):
                if self.websocket.closed:
                    return []
        except Exception:
            return []

        request_id = f"tabs_folder_{uuid.uuid4().hex[:8]}"
        
        future = asyncio.Future()
        self.response_futures[request_id] = future

        try:
            request_msg = {
                "type": "getTabsByFolder",
                "requestId": request_id,
                "folderPath": folder_path,
                "timestamp": int(time.time() * 1000),
                "urgent": True
            }
            
            await self.websocket.send_text(json.dumps(request_msg))

            response = await asyncio.wait_for(future, timeout=timeout)
            tabs = response.get('tabs', [])
            
            # 🔥 CRITICAL FIX: Chỉ trả tabs THỰC SỰ rảnh (canAccept=true và status=free)
            free_tabs = [
                tab for tab in tabs 
                if tab.get('canAccept', False) and tab.get('status') == 'free'
            ]
            
            return free_tabs
            
        except asyncio.TimeoutError:
            return []
        except Exception:
            return []
        finally:
            self.response_futures.pop(request_id, None)

    def handle_available_tabs_response(self, request_id: str, tabs: list):
        future = self.response_futures.get(request_id)
        if not future:
            return
        
        if future.done():
            return
        
        future.set_result({"tabs": tabs})
    
    async def schedule_request_cleanup(self, request_id: str, delay: float = 30.0):
        await asyncio.sleep(delay)
        
        if request_id in self.request_to_tab:
            self.request_to_tab.pop(request_id, None)
    
    async def cleanup_duplicate_detection(self):
        current_time = time.time()
        
        requests_to_remove = []
        for request_id in self.requests_in_progress:
            if len(self.requests_in_progress) > 100:
                requests_to_remove.append(request_id)
        
        for request_id in requests_to_remove:
            self.requests_in_progress.discard(request_id)

        processed_to_remove = []
        for request_id, timestamp in self.processed_requests.items():
            if current_time - timestamp > 600:
                processed_to_remove.append(request_id)
        
        for request_id in processed_to_remove:
            self.processed_requests.pop(request_id, None)
            self.duplicate_count.pop(request_id, None)

    async def _duplicate_cleanup_loop(self):
        while True:
            await asyncio.sleep(300)
            await self.cleanup_duplicate_detection()