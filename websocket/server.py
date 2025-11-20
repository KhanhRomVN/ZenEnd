"""
WebSocket server - Single port version
"""
import asyncio
import websockets

from config.settings import WS_HOST
from .handlers import handle_websocket_connection


async def start_websocket_server(port: int, port_manager):
    # 🆕 Khởi động cleanup loop khi event loop đã sẵn sàng
    await port_manager.start_cleanup_loop()
    
    print(f"[WebSocket] Starting WebSocket server on {WS_HOST}:{port}")
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            async with websockets.serve(
                lambda ws: handle_websocket_connection(ws, port_manager),
                WS_HOST,
                port,
                ping_interval=20,  # Ping every 20s
                ping_timeout=10,   # Wait 10s for pong
                close_timeout=5    # Close timeout 5s
            ):
                print(f"[WebSocket] WebSocket server started successfully on ws://{WS_HOST}:{port}")
                retry_count = 0  # Reset on success
                await asyncio.Future()  # Run forever
        except Exception as e:
            retry_count += 1
            print(f"[WebSocket] ❌ Error starting WebSocket server (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                print(f"[WebSocket] Retrying in {2 ** retry_count} seconds...")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff: 2s, 4s, 8s
            else:
                print(f"[WebSocket] Failed to start WebSocket server after {max_retries} attempts")
                break