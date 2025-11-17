"""
State management cho Tabs và Ports
"""
import time
from typing import Dict, Optional, Tuple
from websockets.server import WebSocketServerProtocol

from .enums import TabStatus


class TabState:
    """Trạng thái chi tiết của mỗi tab"""
    def __init__(self, tab_id: int, container_name: str, title: str, url: str = ""):
        self.tab_id = tab_id
        self.container_name = container_name
        self.title = title
        self.url = url
        self.status = TabStatus.FREE
        self.last_used = 0.0
        self.error_count = 0
        self.current_request_id: Optional[str] = None
        self.last_status_check = 0.0
        
    def can_accept_request(self) -> bool:
        """Kiểm tra tab có thể nhận request mới không"""
        if self.status != TabStatus.FREE:
            return False
        # Tab free ít nhất 2 giây trước khi nhận request mới
        return time.time() - self.last_used >= 2.0
    
    def mark_busy(self, request_id: str):
        """Đánh dấu tab đang bận"""
        self.status = TabStatus.BUSY
        self.current_request_id = request_id
        self.last_used = time.time()
        
    def mark_free(self):
        """Đánh dấu tab rảnh"""
        self.status = TabStatus.FREE
        self.current_request_id = None
        self.last_used = time.time()
        
    def mark_error(self):
        """Đánh dấu tab lỗi"""
        self.status = TabStatus.ERROR
        self.error_count += 1
        self.current_request_id = None
        
    def mark_not_found(self):
        """Đánh dấu tab không tồn tại"""
        self.status = TabStatus.NOT_FOUND
        self.current_request_id = None


class PortState:
    """Trạng thái của mỗi WebSocket port"""
    def __init__(self, port: int):
        self.port = port
        self.is_busy = False
        self.websocket: Optional[WebSocketServerProtocol] = None
        self.tabs: Dict[int, TabState] = {}  # tab_id -> TabState
        self.last_used = 0.0
        self.health_check_interval = 30.0  # 30 giây kiểm tra sức khỏe 1 lần
        
    def update_tabs(self, focused_tabs: list):
        """Cập nhật danh sách tabs từ ZenTab"""
        current_tab_ids = set(self.tabs.keys())
        new_tab_ids = set()
        
        for tab_info in focused_tabs:
            tab_id = tab_info['tabId']
            new_tab_ids.add(tab_id)
            
            if tab_id not in self.tabs:
                # Thêm tab mới
                self.tabs[tab_id] = TabState(
                    tab_id=tab_id,
                    container_name=tab_info.get('containerName', 'Unknown'),
                    title=tab_info.get('title', 'Untitled'),
                    url=tab_info.get('url', '')
                )
                print(f"[Port {self.port}] ➕ Added new tab {tab_id}")
            else:
                # Cập nhật thông tin tab hiện có
                existing_tab = self.tabs[tab_id]
                existing_tab.container_name = tab_info.get('containerName', existing_tab.container_name)
                existing_tab.title = tab_info.get('title', existing_tab.title)
                existing_tab.url = tab_info.get('url', existing_tab.url)
                
                # Nếu tab đang ở trạng thái lỗi nhưng vẫn được gửi từ ZenTab, thử reset
                if existing_tab.status == TabStatus.ERROR:
                    if time.time() - existing_tab.last_used > 60:  # Sau 1 phút thì thử reset
                        existing_tab.status = TabStatus.FREE
                        existing_tab.error_count = 0
                        print(f"[Port {self.port}] 🔄 Reset error tab {tab_id}")
        
        # Xóa các tab không còn tồn tại
        removed_tabs = current_tab_ids - new_tab_ids
        for tab_id in removed_tabs:
            if tab_id in self.tabs:
                del self.tabs[tab_id]
                print(f"[Port {self.port}] 🗑️ Removed tab {tab_id}")
    
    def get_free_tab(self) -> Optional[Tuple[int, TabState]]:
        """Lấy tab rảnh đầu tiên (ưu tiên tab ít lỗi nhất và lâu nhất chưa dùng)"""
        free_tabs = []
        
        for tab_id, tab_state in self.tabs.items():
            if tab_state.can_accept_request():
                free_tabs.append((tab_id, tab_state))
        
        if not free_tabs:
            return None
            
        # Ưu tiên tab ít lỗi nhất, sau đó là tab lâu nhất chưa dùng
        free_tabs.sort(key=lambda x: (x[1].error_count, x[1].last_used))
        return free_tabs[0]
    
    def get_tab_status_summary(self) -> dict:
        """Lấy tổng quan trạng thái các tab trong port"""
        status_count = {status: 0 for status in TabStatus}
        for tab in self.tabs.values():
            status_count[tab.status] += 1
            
        return {
            "total_tabs": len(self.tabs),
            "free_tabs": status_count[TabStatus.FREE],
            "busy_tabs": status_count[TabStatus.BUSY],
            "error_tabs": status_count[TabStatus.ERROR],
            "not_found_tabs": status_count[TabStatus.NOT_FOUND]
        }