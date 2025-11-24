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
    
    async def reconnect_websocket(self):
        async with self.lock:
            try:
                # Đóng connection cũ nếu tồn tại
                if self.websocket:
                    try:
                        # Check method close exists trước khi gọi
                        if hasattr(self.websocket, 'close') and callable(self.websocket.close):
                            # Check xem có đang open không
                            if hasattr(self.websocket, 'state'):
                                from websockets.protocol import State
                                if self.websocket.state == State.OPEN:
                                    await self.websocket.close()
                            else:
                                # Fallback: try to close anyway
                                try:
                                    await self.websocket.close()
                                except:
                                    pass
                    except Exception as close_error:
                        print(f"[PortManager] ⚠️ Could not close old connection: {close_error}")
                
                # DON'T reset websocket to None - extension is still connected!
                await asyncio.sleep(1)
                
                # Check if websocket is still there and valid
                if self.websocket:
                    try:
                        # Try to check connection state
                        if hasattr(self.websocket, 'state'):
                            from websockets.protocol import State
                            if self.websocket.state == State.OPEN:
                                return True
                        else:
                            # If we can't check state, assume it's OK if object exists
                            return True
                    except Exception as e:
                        print(f"[PortManager] ⚠️ Error checking connection state: {e}")
                
                return False
                    
            except Exception as e:
                print(f"[PortManager] ❌ Error in reconnect: {e}")
                import traceback
                traceback.print_exc()
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
            websocket_connected = True  # Có websocket object = connected
            try:
                # Check if websocket is still open
                # Different websocket libraries have different attributes
                if hasattr(self.websocket, 'closed'):
                    websocket_open = not self.websocket.closed
                elif hasattr(self.websocket, 'open'):
                    websocket_open = self.websocket.open
                elif hasattr(self.websocket, 'state'):
                    # For websockets.server.WebSocketServerProtocol
                    from websockets.protocol import State
                    websocket_open = self.websocket.state == State.OPEN
                else:
                    # Fallback: assume open if we have the object
                    websocket_open = True
                    
            except Exception as e:
                print(f"[PortManager] ⚠️ Error checking websocket status: {e}")
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
            dict: Response data từ ZenTab
            
        Raises:
            asyncio.TimeoutError: Nếu quá timeout chưa nhận được response
            HTTPException: Nếu response chứa error
        """
        # Tạo future để chờ response
        future = asyncio.Future()
        self.response_futures[request_id] = future
        
        try:
            # Đợi response với timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            
            # Kiểm tra response có lỗi không
            if "error" in response:
                from fastapi import HTTPException
                error_msg = response["error"]
                
                # Xử lý các loại lỗi khác nhau
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    raise HTTPException(status_code=503, detail=error_msg)
                else:
                    raise HTTPException(status_code=500, detail=error_msg)
            
            return response
            
        except asyncio.TimeoutError:
            # Cleanup khi timeout
            self.response_futures.pop(request_id, None)
            self.request_to_tab.pop(request_id, None)
            
            # 🔥 FIX: Trả về dict error thay vì StreamingResponse
            from fastapi import HTTPException
            raise HTTPException(
                status_code=504,
                detail=f"Request đã timeout sau {timeout} giây. DeepSeek mất quá nhiều thời gian để phản hồi."
            )
            
        except Exception as e:
            # Cleanup khi có lỗi
            self.response_futures.pop(request_id, None)
            self.request_to_tab.pop(request_id, None)
            raise
            
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
        Tăng timeout lên 10s để đảm bảo đủ thời gian cho ZenTab phản hồi
        """
        if not self.websocket:
            return []
        
        try:
            # Check websocket state properly
            if hasattr(self.websocket, 'state'):
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
            
            await self.websocket.send(json.dumps(request_msg))

            response = await asyncio.wait_for(future, timeout=timeout)
            tabs = response.get('tabs', [])
            
            return tabs
            
        except asyncio.TimeoutError:
            return []
        except Exception:
            return []
        finally:
            self.response_futures.pop(request_id, None)

    async def request_tabs_by_folder(self, folder_path: str, timeout: float = 10.0) -> list:
        """
        Request danh sách tabs có folder_path khớp từ ZenTab.
        Dùng cho các request KHÔNG phải new task.
        """
        if not self.websocket:
            return []
        
        try:
            # Check websocket state properly
            if hasattr(self.websocket, 'state'):
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
            
            await self.websocket.send(json.dumps(request_msg))

            response = await asyncio.wait_for(future, timeout=timeout)
            tabs = response.get('tabs', [])
            
            return tabs
            
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