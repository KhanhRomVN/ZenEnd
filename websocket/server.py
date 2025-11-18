"""
WebSocket server - Single port version
"""
import asyncio
import websockets

from config.settings import WS_HOST
from .handlers import handle_websocket_connection


async def start_websocket_server(port: int, port_manager):
    """Khởi động WebSocket server duy nhất trên port 1500"""
    print(f"[WS:Server] 🚀 Starting WebSocket server with PortManager: {id(port_manager)}")
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
                print(f"[WS:{port}] 🚀 WebSocket server started (attempt {retry_count + 1})")
                retry_count = 0  # Reset on success
                await asyncio.Future()  # Run forever
        except Exception as e:
            retry_count += 1
            print(f"[WS:{port}] ❌ Failed to start (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff: 2s, 4s, 8s
            else:
                print(f"[WS:{port}] 💀 Max retries reached, giving up")
                break