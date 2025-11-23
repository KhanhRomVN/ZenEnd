"""
Cấu hình tập trung cho ZenEnd
"""
import os

API_KEY = os.getenv("API_KEY", "THIS_IS_API_KEY")

# Production: Dùng $PORT từ Render, Local: dùng 3030
HTTP_PORT = int(os.getenv("PORT", 3030))
HTTP_HOST = "0.0.0.0"

# WebSocket KHÔNG CẦN trên production (chỉ dùng local với ZenTab extension)
WS_PORT = int(os.getenv("WS_PORT", 1500))
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")

REQUEST_TIMEOUT = 180  # 3 phút timeout