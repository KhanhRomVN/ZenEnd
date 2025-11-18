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
        """Singleton pattern - chỉ tạo 1 instance duy nhất"""
        if cls._instance is None:
            print("[PortManager] 🏗️ Creating new PortManager instance (Singleton)")
            cls._instance = super().__new__(cls)
            cls._lock = asyncio.Lock()
            cls._instance._initialized = False
        else:
            print("[PortManager] ♻️ Returning existing PortManager instance (Singleton)")
        return cls._instance
    
    def __init__(self):
        # Chỉ khởi tạo một lần duy nhất
        if self._initialized:
            print("[PortManager] ⏩ Already initialized, skipping __init__")
            return
            
        print("[PortManager] 🔧 Initializing PortManager attributes")
        self.websocket: Optional[object] = None
        self.port: int = WS_PORT
        
        self.global_tab_pool: Dict[int, TabState] = {}
        
        self.response_futures: Dict[str, asyncio.Future] = {}
        self.request_to_tab: Dict[str, int] = {}
        self.temp_tab_states: Dict[int, TabState] = {}
        
        self.lock = asyncio.Lock()
        self.connection_time = 0
        
        self._initialized = True
        print("[PortManager] ✅ PortManager initialized successfully")
    
    def get_connection_status(self) -> dict:
        """Debug: Lấy trạng thái chi tiết của connection"""
        print(f"[PortManager] 🔍 get_connection_status called")
        print(f"[PortManager]   - self.websocket: {self.websocket}")
        print(f"[PortManager]   - self.websocket is None: {self.websocket is None}")
        
        websocket_open = False
        if self.websocket:
            try:
                websocket_open = self.websocket.open
                print(f"[PortManager]   - self.websocket.open: {websocket_open}")
            except Exception as e:
                websocket_open = False
                print(f"[PortManager]   - Error checking websocket.open: {e}")
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
        
        print(f"[PortManager] 📊 Connection status: {status}")
        return status
    
    # 🆕 THÊM: Method để cập nhật websocket một cách an toàn
    async def update_websocket(self, websocket):
        """Cập nhật websocket connection một cách an toàn"""
        print(f"[PortManager] 🔧 update_websocket called")
        print(f"[PortManager]   - Before: self.websocket is None = {self.websocket is None}")
        print(f"[PortManager]   - New websocket object: {websocket}")
        print(f"[PortManager]   - New websocket is open: {websocket.open}")
        
        async with self.lock:
            self.websocket = websocket
            self.connection_time = time.time()
            print(f"[PortManager] ✅ WebSocket updated successfully")
            print(f"[PortManager]   - After: self.websocket is None = {self.websocket is None}")
            print(f"[PortManager]   - After: self.websocket is open = {self.websocket.open}")
            print(f"[PortManager]   - Connection time: {self.connection_time}")
    
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
                print(f"[PortManager] Failed to broadcast status: {e}")
        
    async def get_free_tab(self) -> Optional[Tuple[int, TabState]]:
        """
        Tìm 1 tab FREE trong global pool
        Trả về: (tab_id, tab_state)
        """
        async with self.lock:
            # 🆕 FIX: Kiểm tra tabs có sẵn TRƯỚC khi check WebSocket
            # Cho phép sử dụng tabs đã được cache từ connection trước
            if len(self.global_tab_pool) == 0:
                print("[PortManager] ❌ No tabs in global pool")
                return None
            
            # Lọc tabs FREE trong global pool
            free_tabs = [
                (tid, ts) for tid, ts in self.global_tab_pool.items()
                if ts.can_accept_request()
            ]
            
            if not free_tabs:
                print("[PortManager] ❌ No free tabs available in global pool")
                return None
            
            # Sort tabs: ưu tiên tab ít lỗi và lâu chưa dùng
            free_tabs.sort(key=lambda x: (x[1].error_count, x[1].last_used))
            tab_id, tab_state = free_tabs[0]
            
            print(f"[PortManager] ✅ Selected: Tab {tab_id} ({tab_state.container_name})")
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
            
            print(f"[PortManager] 🧹 Starting cleanup process...")
            
            if self.websocket:
                try:
                    await self.websocket.send(json.dumps(cleanup_message))
                    print(f"[PortManager] 📤 Sent cleanup command to WebSocket")
                except Exception as send_error:
                    print(f"[PortManager] ⚠️ Failed to send cleanup: {send_error}")
            else:
                print("[PortManager] ⚠️ WARNING: WebSocket not connected for cleanup")
            
        except Exception as e:
            print(f"[PortManager] ❌ Failed to cleanup wsMessages: {e}")
        # 🆕 THÊM: Method yêu cầu danh sách tabs mới từ ZenTab
    async def request_fresh_tabs(self, timeout: float = 5.0) -> Optional[list]:
        """Yêu cầu và chờ danh sách tabs mới từ ZenTab"""
        print(f"[PortManager] 🎯 request_fresh_tabs called")
        print(f"[PortManager]   - self.websocket: {self.websocket}")
        print(f"[PortManager]   - self.websocket is None: {self.websocket is None}")
        
        if not self.websocket:
            print("[PortManager] ❌ No WebSocket connection to request tabs")
            print("[PortManager]   - This means update_websocket was not called, or websocket was cleared")
            return None
        
        print(f"[PortManager] ✅ WebSocket exists, checking if open...")

        # 🔧 FIX: Check WebSocket is still open
        try:
            if self.websocket.closed:
                print("[PortManager] ❌ WebSocket connection is closed")
                return None
        except Exception as e:
            print(f"[PortManager] ❌ Cannot check WebSocket state: {e}")
            return None

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
            
            print(f"[PortManager] 🔍 Attempting to send getAvailableTabs via WebSocket")
            print(f"[PortManager]   - WebSocket state: open={not self.websocket.closed}")
            print(f"[PortManager]   - Request ID: {request_id}")
            print(f"[PortManager]   - Message: {request_msg}")
            
            await self.websocket.send(json.dumps(request_msg))
            print(f"[PortManager] ✅ Message sent successfully to extension")
            print(f"[PortManager] 📡 Sent fresh tabs request: {request_id}")

            # Chờ response với timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            print(f"[PortManager] ✅ Received fresh tabs: {len(response.get('tabs', []))} tabs")
            return response.get('tabs', [])
            
        except asyncio.TimeoutError:
            print(f"[PortManager] ❌ Timeout waiting for fresh tabs")
            return None
        except Exception as e:
            print(f"[PortManager] ❌ Error requesting fresh tabs: {e}")
            return None
        finally:
            self.response_futures.pop(request_id, None)

    # 🆕 THÊM: Xử lý response availableTabs
    def handle_available_tabs_response(self, request_id: str, tabs: list):
        """Xử lý response danh sách tabs từ ZenTab"""
        future = self.response_futures.get(request_id)
        if future and not future.done():
            future.set_result({"tabs": tabs})

    # 🆕 SỬA: Method get_free_tab không dùng global pool nữa
    async def get_free_tab(self) -> Optional[Tuple[int, TabState]]:
        """KHÔNG DÙNG NỮA - Sẽ luôn trả về None để buộc dùng request_fresh_tabs"""
        return None

    # 🆕 THÊM: Lấy tab state tạm thời
    def get_temp_tab_state(self, tab_id: int) -> Optional[TabState]:
        """Lấy tab state tạm thời cho request hiện tại"""
        return self.temp_tab_states.get(tab_id)

    # 🆕 THÊM: Cleanup tab state tạm thời
    def cleanup_temp_tab_state(self, tab_id: int):
        """Dọn dẹp tab state tạm thời"""
        self.temp_tab_states.pop(tab_id, None)