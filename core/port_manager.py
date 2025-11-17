"""
Port Manager - Quản lý trạng thái và phân bổ ports
"""
import asyncio
from typing import Dict, Optional, Tuple

from fastapi import HTTPException

from config.settings import WS_PORTS
from models import TabStatus, PortState, TabState


class PortManager:
    """Quản lý trạng thái và phân bổ ports với cơ chế thông minh"""
    def __init__(self):
        self.ports: Dict[int, PortState] = {port: PortState(port) for port in WS_PORTS}
        self.response_futures: Dict[str, asyncio.Future] = {}
        self.request_to_tab: Dict[str, Tuple[int, int]] = {}  # request_id -> (port, tab_id)
        self.lock = asyncio.Lock()
        
    async def get_free_tab(self) -> Optional[Tuple[int, int, PortState, TabState]]:
        """Lấy tab rảnh từ tất cả ports (ưu tiên port có nhiều tab rảnh nhất)"""
        async with self.lock:
            available_ports = []
            
            for port, port_state in self.ports.items():
                if not port_state.websocket:
                    continue
                    
                tab_info = port_state.get_free_tab()
                if tab_info:
                    tab_id, tab_state = tab_info
                    status_summary = port_state.get_tab_status_summary()
                    available_ports.append((port, tab_id, port_state, tab_state, status_summary['free_tabs']))
            
            if not available_ports:
                return None
                
            # Ưu tiên port có nhiều tab rảnh nhất
            available_ports.sort(key=lambda x: x[4], reverse=True)
            port, tab_id, port_state, tab_state, _ = available_ports[0]
            
            return (port, tab_id, port_state, tab_state)
    
    def get_busy_count(self) -> int:
        """Đếm số tab đang busy"""
        count = 0
        for port_state in self.ports.values():
            for tab in port_state.tabs.values():
                if tab.status == TabStatus.BUSY:
                    count += 1
        return count
    
    def get_connected_count(self) -> int:
        """Đếm số port đã kết nối WebSocket"""
        return sum(1 for p in self.ports.values() if p.websocket)
    
    def get_total_free_tabs(self) -> int:
        """Đếm tổng số tab rảnh"""
        count = 0
        for port_state in self.ports.values():
            for tab in port_state.tabs.values():
                if tab.can_accept_request():
                    count += 1
        return count
    
    def get_detailed_status(self) -> dict:
        """Lấy trạng thái chi tiết của tất cả ports"""
        status = {}
        for port, port_state in self.ports.items():
            status[port] = {
                "connected": port_state.websocket is not None,
                "tabs": port_state.get_tab_status_summary()
            }
        return status
    
    async def wait_for_response(self, request_id: str, timeout: float) -> dict:
        """Chờ response từ ZenTab"""
        future = asyncio.Future()
        self.response_futures[request_id] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            # Timeout: đánh dấu tab rảnh lại
            if request_id in self.request_to_tab:
                port, tab_id = self.request_to_tab[request_id]
                if port in self.ports and tab_id in self.ports[port].tabs:
                    self.ports[port].tabs[tab_id].mark_free()
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