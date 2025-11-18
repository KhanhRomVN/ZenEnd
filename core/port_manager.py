"""
Port Manager - Quản lý trạng thái tabs và WebSocket connection duy nhất
"""
import uuid
import json
import time
import asyncio
from typing import Dict, Optional, Tuple

from fastapi import HTTPException

from config.settings import WS_PORT
from models import TabStatus, TabState


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
        self.port: int = WS_PORT
        
        self.global_tab_pool: Dict[int, TabState] = {}
        
        self.response_futures: Dict[str, asyncio.Future] = {}
        self.request_to_tab: Dict[str, int] = {}
        self.temp_tab_states: Dict[int, TabState] = {}
        self.processed_requests: Dict[str, float] = {}
        self.duplicate_count: Dict[str, int] = {}
        self.requests_in_progress: set[str] = set()
        
        self.lock = asyncio.Lock()
        self.connection_time = 0
        
        self._initialized = True
        self._cleanup_task = None
        
        self.forwarded_messages: Dict[str, float] = {}
        self.message_processing_log: Dict[str, list] = {}

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
                tab_id = self.request_to_tab[request_id]
                self.cleanup_temp_tab_state(tab_id)
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
            if current_time - timestamp > 300:
                keys_to_remove.append(req_id)
        
        for req_id in keys_to_remove:
            self.processed_requests.pop(req_id, None)
            self.duplicate_count.pop(req_id, None)
    
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
            try:
                websocket_open = getattr(self.websocket, 'open', False)
                websocket_connected = True
            except Exception:
                websocket_open = False
                websocket_connected = False
                
        status = {
            "websocket_connected": websocket_connected,
            "websocket_open": websocket_open,
            "total_tabs": len(self.global_tab_pool),
            "free_tabs": self.get_total_free_tabs(),
            "busy_tabs": self.get_busy_count(),
            "port": self.port,
            "connection_age": time.time() - self.connection_time if self.connection_time > 0 else 0
        }
        
        return status
    
    async def update_websocket(self, websocket):
        async with self.lock:
            self.websocket = websocket
            self.connection_time = time.time()
    
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
        
    async def get_free_tab(self) -> Optional[Tuple[int, TabState]]:
        async with self.lock:
            if len(self.global_tab_pool) == 0:
                return None
            
            free_tabs = [
                (tid, ts) for tid, ts in self.global_tab_pool.items()
                if ts.can_accept_request()
            ]
            
            if not free_tabs:
                return None
            
            free_tabs.sort(key=lambda x: (x[1].error_count, x[1].last_used))
            tab_id, tab_state = free_tabs[0]
            
            return (tab_id, tab_state)
    
    def get_busy_count(self) -> int:
        return sum(1 for ts in self.global_tab_pool.values() if ts.status == TabStatus.BUSY)
    
    def is_connected(self) -> bool:
        return len(self.global_tab_pool) > 0
    
    def get_total_free_tabs(self) -> int:
        return sum(1 for ts in self.global_tab_pool.values() if ts.can_accept_request())
    
    def get_detailed_status(self) -> dict:
        tabs_status = []
        for tab_id, tab_state in sorted(self.global_tab_pool.items()):
            tabs_status.append({
                "tab_id": tab_id,
                "container_name": tab_state.container_name,
                "title": tab_state.title,
                "status": tab_state.status.value,
                "error_count": tab_state.error_count,
                "can_accept": tab_state.can_accept_request()
            })
        
        return {
            "websocket_connected": self.websocket is not None,
            "tabs": tabs_status
        }
    
    async def wait_for_response(self, request_id: str, timeout: float) -> dict:
        future = asyncio.Future()
        self.response_futures[request_id] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            if request_id in self.request_to_tab:
                tab_id = self.request_to_tab[request_id]
                self.cleanup_temp_tab_state(tab_id)
                del self.request_to_tab[request_id]
            raise HTTPException(status_code=504, detail="Request timeout - AI took too long to respond")
        finally:
            self.response_futures.pop(request_id, None)
    
    def resolve_response(self, request_id: str, response: dict):
        future = self.response_futures.get(request_id)
        
        if future and not future.done():
            try:
                future.set_result(response)
            except Exception:
                pass

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

    async def request_fresh_tabs(self, timeout: float = 5.0) -> list:
        if not self.websocket:
            return []
        
        try:
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
                "timestamp": time.time(),
                "urgent": True
            }
            
            await self.websocket.send(json.dumps(request_msg))

            response = await asyncio.wait_for(future, timeout=timeout)
            return response.get('tabs', [])
            
        except asyncio.TimeoutError:
            return []
        except Exception:
            return []
        finally:
            self.response_futures.pop(request_id, None)

    def handle_available_tabs_response(self, request_id: str, tabs: list):
        future = self.response_futures.get(request_id)
        if future and not future.done():
            future.set_result({"tabs": tabs})

    def get_temp_tab_state(self, tab_id: int) -> Optional[TabState]:
        return self.temp_tab_states.get(tab_id)

    def cleanup_temp_tab_state(self, tab_id: int):
        self.temp_tab_states.pop(tab_id, None)
    
    async def schedule_request_cleanup(self, request_id: str, delay: float = 30.0):
        await asyncio.sleep(delay)
        
        if request_id in self.request_to_tab:
            self.request_to_tab.pop(request_id, None)

    async def schedule_temp_tab_cleanup(self, tab_id: int, delay: float = 60.0):
        await asyncio.sleep(delay)
        
        if tab_id in self.temp_tab_states:
            self.temp_tab_states.pop(tab_id, None)
    
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