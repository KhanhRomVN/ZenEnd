"""
Logger với color và format chuẩn cho ZenEnd
Hỗ trợ cả log console và log response (Cline API format)
"""
import os
import sys
import json
import time
import uuid
import traceback
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum


# Toggle để bật/tắt log
ENABLE_LOGGING = True  # Set False để tắt toàn bộ log


class LogLevel(Enum):
    """Log levels với màu sắc tương ứng"""
    DEBUG = ("DEBUG", "\033[36m")    # Cyan
    INFO = ("INFO", "\033[32m")      # Green
    WARNING = ("WARNING", "\033[33m") # Yellow
    ERROR = ("ERROR", "\033[31m")    # Red
    CRITICAL = ("CRITICAL", "\033[35m") # Magenta


class Logger:
    """Logger với color và format chuẩn"""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    @staticmethod
    def _get_caller_info() -> tuple[str, int]:
        """Lấy thông tin file và line number của caller"""
        try:
            # Lấy stack frame (bỏ qua internal frames)
            frame = sys._getframe(3)  # Skip: _log -> debug/info/error -> caller
            
            filepath = frame.f_code.co_filename
            lineno = frame.f_lineno
            
            # Convert sang relative path từ project root
            try:
                project_root = Path(__file__).parent.parent
                rel_path = Path(filepath).relative_to(project_root)
                return str(rel_path), lineno
            except ValueError:
                # Nếu không relative được, trả về basename
                return os.path.basename(filepath), lineno
                
        except Exception:
            return "unknown", 0
    
    @staticmethod
    def _format_metadata(metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata thành string ngắn gọn"""
        if not metadata:
            return ""
        
        try:
            # Format metadata dạng key=value
            parts = []
            for key, value in metadata.items():
                if isinstance(value, str):
                    parts.append(f"{key}={value}")
                elif isinstance(value, (int, float, bool)):
                    parts.append(f"{key}={value}")
                else:
                    parts.append(f"{key}={type(value).__name__}")
            
            return " ".join(parts)
        except Exception:
            return str(metadata)
    
    @staticmethod
    def _log(
        level: LogLevel,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        show_traceback: bool = False
    ):
        """Internal log function"""
        if not ENABLE_LOGGING:
            return
        
        level_name, level_color = level.value
        filepath, lineno = Logger._get_caller_info()
        
        # Format: [LEVEL] [file:line] message metadata
        log_parts = [
            f"{level_color}{Logger.BOLD}[{level_name}]{Logger.RESET}",
            f"{Logger.DIM}[{filepath}:{lineno}]{Logger.RESET}",
            message
        ]
        
        if metadata:
            meta_str = Logger._format_metadata(metadata)
            if meta_str:
                log_parts.append(f"{Logger.DIM}{meta_str}{Logger.RESET}")
        
        print(" ".join(log_parts), flush=True)
        
        # Hiển thị traceback nếu được yêu cầu
        if show_traceback:
            tb_lines = traceback.format_exc()
            if tb_lines and "NoneType: None" not in tb_lines:
                print(f"{Logger.DIM}{tb_lines}{Logger.RESET}", flush=True)
    
    @staticmethod
    def debug(message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log DEBUG level"""
        Logger._log(LogLevel.DEBUG, message, metadata)
    
    @staticmethod
    def info(message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log INFO level"""
        Logger._log(LogLevel.INFO, message, metadata)
    
    @staticmethod
    def warning(message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log WARNING level"""
        Logger._log(LogLevel.WARNING, message, metadata)
    
    @staticmethod
    def error(
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        show_traceback: bool = False
    ):
        """Log ERROR level"""
        Logger._log(LogLevel.ERROR, message, metadata, show_traceback)
    
    @staticmethod
    def critical(
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        show_traceback: bool = True
    ):
        """Log CRITICAL level (luôn hiển thị traceback)"""
        Logger._log(LogLevel.CRITICAL, message, metadata, show_traceback)
    
    @staticmethod
    def error_response(
        error_message: str,
        detail_message: str,
        metadata: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
        show_traceback: bool = True
    ):
        """
        Log lỗi VÀ trả về StreamingResponse với SSE format (Cline-compatible)
        
        Returns:
            StreamingResponse với format SSE
        """
        from fastapi.responses import StreamingResponse
        """
        Log lỗi VÀ trả về Cline API Response format
        
        Args:
            error_message: Thông báo lỗi ngắn gọn (xuất hiện trong log)
            detail_message: Thông báo chi tiết (xuất hiện trong response content)
            metadata: Metadata bổ sung cho log
            status_code: HTTP status code để client biết cách xử lý
            show_traceback: Có hiển thị traceback trong log không
            
        Returns:
            Dict chứa OpenAI completion response với attempt_completion format (Cline-compatible)
        """
        # Log lỗi ra console
        Logger._log(
            LogLevel.ERROR if status_code < 500 else LogLevel.CRITICAL,
            error_message,
            metadata,
            show_traceback
        )
        
        # Phân loại lỗi dựa trên status_code
        error_type_map = {
            400: "Yêu cầu không hợp lệ",
            401: "Xác thực thất bại",
            403: "Không có quyền truy cập",
            404: "Không tìm thấy tài nguyên",
            408: "Timeout",
            429: "Quá nhiều yêu cầu",
            500: "Lỗi máy chủ nội bộ",
            502: "Bad Gateway",
            503: "Dịch vụ không khả dụng",
            504: "Gateway Timeout"
        }
        
        error_type = error_type_map.get(status_code, "Lỗi không xác định")
        
        # Format metadata để hiển thị trong error message
        metadata_str = ""
        if metadata:
            metadata_lines = []
            for key, value in metadata.items():
                metadata_lines.append(f"  • {key}: {value}")
            if metadata_lines:
                metadata_str = f"\n\nChi tiết kỹ thuật:\n" + "\n".join(metadata_lines)
        
        # Tạo response content THEO FORMAT CLINE (giống attempt_completion thành công)
        content = f"""Đã xảy ra lỗi trong quá trình xử lý yêu cầu

Loại lỗi: {error_type} (HTTP {status_code})

Mô tả chi tiết:
{detail_message}

Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}{metadata_str}

---

Khuyến nghị:
- Vui lòng kiểm tra lại yêu cầu và thử lại
- Nếu lỗi vẫn tiếp diễn, hãy kiểm tra log chi tiết hoặc liên hệ hỗ trợ
<attempt_completion>
<result>
Lỗi: {error_type} - {detail_message}

Status Code: {status_code}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
</result>
</attempt_completion>"""
        
        # Tạo OpenAI completion response (Cline-compatible format)
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(content.split()),
                "total_tokens": len(content.split())
            },
            "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
        }
        
        # 🆕 Print toàn bộ response JSON (pretty format) để debug
        print(f"\n{Logger.BOLD}{'='*80}{Logger.RESET}")
        print(f"{Logger.BOLD}{Logger.DIM}[ERROR RESPONSE JSON]{Logger.RESET}")
        print(f"{Logger.BOLD}{'='*80}{Logger.RESET}")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print(f"{Logger.BOLD}{'='*80}{Logger.RESET}\n")
        
        # Trả về SSE stream format giống response thành công
        async def generate_error():
            # Yield từng chunk riêng biệt với delay nhỏ
            yield f"data: {json.dumps(response)}\n\n".encode('utf-8')
            yield "data: [DONE]\n\n".encode('utf-8')
        
        return StreamingResponse(
            generate_error(),
            media_type="text/event-stream",
            status_code=200  # ⚠️ CRITICAL: Phải dùng 200 cho SSE, không phải status_code gốc
        )


# Convenience functions để import dễ dàng
debug = Logger.debug
info = Logger.info
warning = Logger.warning
error = Logger.error
critical = Logger.critical
error_response = Logger.error_response


# Example usage
if __name__ == "__main__":
    # Test các log levels
    debug("Debug message", {"request_id": "test-123"})
    info("Server started", {"port": 3030, "host": "0.0.0.0"})
    warning("Request timeout", {"timeout": 30, "request_id": "abc"})
    error("Database connection failed", {"retry_count": 3}, show_traceback=False)
    critical("Fatal error", {"component": "websocket"})
    
    # Test error response
    print("\n--- Error Response Test ---")
    response = error_response(
        error_message="WebSocket not connected",
        detail_message="Không thể kết nối tới ZenTab extension. Vui lòng đảm bảo extension đang chạy.",
        metadata={"port": 1500, "retry_count": 3},
        status_code=503,
        show_traceback=False
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))