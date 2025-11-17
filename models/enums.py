"""
Enums cho trạng thái tab
"""
from enum import Enum


class TabStatus(Enum):
    FREE = "free"           # Tab rảnh, sẵn sàng nhận request
    BUSY = "busy"           # Tab đang xử lý request
    ERROR = "error"         # Tab có lỗi, tạm thời không dùng được
    NOT_FOUND = "not_found" # Tab không tồn tại