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
    _instance = None  # 🆕 Singleton instance
    _lock = None  # 🆕 Class-level lock for thread-safety
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._lock = asyncio.Lock()
            cls._instance._initialized = False
        
        return cls._instance
    
    def __init__(self):
        # Chỉ khởi tạo một lần duy nhất
        if self._initialized:
            return
            
        self.websocket: Optional[object] = None
        self.port: int = WS_PORT
        
        self.global_tab_pool: Dict[int, TabState] = {}
        
        self.response_futures: Dict[str, asyncio.Future] = {}
        self.request_to_tab: Dict[str, int] = {}
        self.temp_tab_states: Dict[int, TabState] = {}
        
        self.lock = asyncio.Lock()
        self.connection_time = 0
        
        self._initialized = True
    
    def get_connection_status(self) -> dict:        
        websocket_open = False
        if self.websocket:
            try:
                websocket_open = self.websocket.open
            except Exception as e:
                websocket_open = False
        else:
            print(f"[PortManager]   - self.websocket is None, cannot check open state")
                
        status = {
            "websocket_connected": self.websocket is not None,
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
        """Broadcast status update tới WebSocket client"""
        if self.websocket:
            try:
                status_data = {
                    "type": "statusUpdate",
                    "data": self.get_detailed_status(),
                    "timestamp": time.time()
                }
                await self.websocket.send(json.dumps(status_data))
            except Exception as e:
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
            
            # Sort tabs: ưu tiên tab ít lỗi và lâu chưa dùng
            free_tabs.sort(key=lambda x: (x[1].error_count, x[1].last_used))
            tab_id, tab_state = free_tabs[0]
            
            return (tab_id, tab_state)
    
    def get_busy_count(self) -> int:
        """Đếm số tab đang BUSY"""
        return sum(1 for ts in self.global_tab_pool.values() if ts.status == TabStatus.BUSY)
    
    def is_connected(self) -> bool:
        """Kiểm tra có tabs khả dụng không (dù WebSocket có disconnect)"""
        # 🆕 FIX: Check tabs thay vì WebSocket - tabs vẫn valid sau disconnect
        return len(self.global_tab_pool) > 0
    
    def get_total_free_tabs(self) -> int:
        """Đếm số tab FREE trong global pool"""
        return sum(1 for ts in self.global_tab_pool.values() if ts.can_accept_request())
    
    def get_detailed_status(self) -> dict:
        """Lấy trạng thái chi tiết của WebSocket và tabs"""
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
        """Chờ response từ ZenTab"""
        future = asyncio.Future()
        self.response_futures[request_id] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            if request_id in self.request_to_tab:
                tab_id = self.request_to_tab[request_id]
                # 🆕 SỬA: Cleanup temp tab state thay vì global pool
                self.cleanup_temp_tab_state(tab_id)
                del self.request_to_tab[request_id]
            raise HTTPException(status_code=504, detail="Request timeout - AI took too long to respond")
        finally:
            self.response_futures.pop(request_id, None)
            self.request_to_tab.pop(request_id, None)
    
    def resolve_response(self, request_id: str, response: dict):
        """Trả response về cho request đang chờ"""
        future = self.response_futures.get(request_id)
        if future and not future.done():
            future.set_result(response)

    async def cleanup_pending_messages(self):
        """
        Cleanup wsMessages trong storage để tránh prompt cũ bị broadcast tới tất cả tabs.
        """
        try:
            cleanup_message = {
                "type": "cleanupMessages",
                "timestamp": time.time(),
                "force": True
            }
                        
            if self.websocket:
                try:
                    await self.websocket.send(json.dumps(cleanup_message))
                except Exception as send_error:
                    print(f"[PortManager] ⚠️ Failed to send cleanup: {send_error}")
            
        except Exception as e:
            print(f"[PortManager] ❌ Failed to cleanup wsMessages: {e}")

    async def request_fresh_tabs(self, timeout: float = 5.0) -> list:
        if not self.websocket:
            return []
        
        try:
            if self.websocket.closed:
                return []
        except Exception as e:
            return []

        # Tạo request ID duy nhất
        request_id = f"tabs_req_{uuid.uuid4().hex[:8]}"
        future = asyncio.Future()
        self.response_futures[request_id] = future

        try:
            # Gửi yêu cầu tabs mới
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
        except Exception as e:
            return []
        finally:
            self.response_futures.pop(request_id, None)

    def handle_available_tabs_response(self, request_id: str, tabs: list):
        future = self.response_futures.get(request_id)
        if future and not future.done():
            future.set_result({"tabs": tabs})

    async def get_free_tab(self) -> Optional[Tuple[int, TabState]]:
        return None

    def get_temp_tab_state(self, tab_id: int) -> Optional[TabState]:
        return self.temp_tab_states.get(tab_id)

    def cleanup_temp_tab_state(self, tab_id: int):
        """Dọn dẹp tab state tạm thời"""
        self.temp_tab_states.pop(tab_id, None)