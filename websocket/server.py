"""
WebSocket server
"""
import asyncio
import websockets

from config.settings import WS_HOST
from .handlers import handle_websocket_connection


async def start_websocket_server(port: int, port_manager):
    """Khởi động WebSocket server cho một port"""
    try:
        async with websockets.serve(
            lambda ws: handle_websocket_connection(ws, port, port_manager),
            WS_HOST,
            port
        ):
            await asyncio.Future()  # Chạy mãi mãi
    except Exception as e:
        print(f"[WS:{port}] ❌ Failed to start: {e}")