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