"""
WebSocket server - Single port version
"""
import asyncio
import websockets
import time
from typing import Set

from config.settings import WS_HOST
from .handlers import handle_websocket_connection


class WebSocketServer:
    def __init__(self, port: int, port_manager):
        self.port = port
        self.port_manager = port_manager
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.start_time = time.time()
        self.total_connections = 0
        self.failed_connections = 0
        
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol):
        """Wrapper để track connections"""
        self.active_connections.add(websocket)
        self.total_connections += 1
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        try:
            await handle_websocket_connection(websocket, self.port_manager)
        except Exception as e:
            self.failed_connections += 1
        finally:
            self.active_connections.discard(websocket)
    
    async def health_monitor(self):
        """Monitor server health and log statistics"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                uptime = time.time() - self.start_time
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[WS Server:{self.port}] Health monitor error: {e}")
    
    async def start(self):
        """Start WebSocket server with auto-reconnect"""
        retry_count = 0
        max_retries = 5
        base_delay = 2
        
        # Start health monitor
        health_task = asyncio.create_task(self.health_monitor())
        
        while retry_count < max_retries:
            try:                
                self.server = await websockets.serve(
                    self.handle_client,
                    WS_HOST,
                    self.port,
                    ping_interval=20,      # Ping every 20s to keep alive
                    ping_timeout=10,       # Wait 10s for pong response
                    close_timeout=5,       # Close timeout 5s
                    max_size=10 * 1024 * 1024,  # 10MB max message size
                    compression=None       # Disable compression for better performance
                )
                
                retry_count = 0  # Reset retry counter on success
                
                # Keep server running
                await asyncio.Future()
                
            except OSError as e:
                if "Address already in use" in str(e):
                    break  # Don't retry on port conflicts
                else:
                    retry_count += 1
                    delay = base_delay ** retry_count  # Exponential backoff: 2s, 4s, 8s, 16s, 32s
                    
                    if retry_count < max_retries:
                        await asyncio.sleep(delay)
                    else:
                        break
                        
            except asyncio.CancelledError:
                break
                
            except Exception as e:
                retry_count += 1
                delay = base_delay ** retry_count
                
                if retry_count < max_retries:
                    await asyncio.sleep(delay)
                else:
                    break
        
        # Cleanup
        health_task.cancel()
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all active connections gracefully
        if self.active_connections:
            await asyncio.gather(
                *[conn.close() for conn in self.active_connections],
                return_exceptions=True
            )
            
    def get_stats(self):
        """Get server statistics"""
        return {
            'port': self.port,
            'active_connections': len(self.active_connections),
            'total_connections': self.total_connections,
            'failed_connections': self.failed_connections,
            'uptime': time.time() - self.start_time,
            'running': self.server is not None
        }


async def start_websocket_server(port: int, port_manager):
    """Start WebSocket server with enhanced features"""
    # Khởi động cleanup loop
    await port_manager.start_cleanup_loop()
    
    # Create and start server
    server = WebSocketServer(port, port_manager)
    await server.start()