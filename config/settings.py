"""
Cấu hình tập trung cho ZenEnd
"""
import os

API_KEY = os.getenv("API_KEY", "THIS_IS_API_KEY")

# WebSocket và HTTP API chạy trên CÙNG PORT
HTTP_PORT = int(os.getenv("PORT", 3030))
HTTP_HOST = "0.0.0.0"

REQUEST_TIMEOUT = 1500