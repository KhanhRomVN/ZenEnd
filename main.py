"""
ZenEnd Backend - Main Server
Chạy 10 WebSocket servers (1501-1510) và HTTP API để bridge với ZenTab
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from config.settings import WS_PORT, HTTP_PORT, HTTP_HOST, API_KEY
from core import PortManager
from api.routes import setup_routes
from websocket import start_websocket_server


# ============================================================================
# GLOBAL INSTANCES (Singleton)
# ============================================================================
print("[Main] 🚀 Creating PortManager instance...")
port_manager = PortManager()
print(f"[Main] ✅ PortManager created: {id(port_manager)}")


# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    # Startup: Khởi động WebSocket server duy nhất
    ws_task = asyncio.create_task(start_websocket_server(WS_PORT, port_manager))
    
    yield
    
    # Shutdown: Cancel WebSocket task
    ws_task.cancel()


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title="ZenEnd",
    version="1.0.0",
    lifespan=lifespan
)

# Setup routes với port_manager dependency
setup_routes(app, port_manager)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level="info",
        reload=True,
        reload_dirs=["./"]
    )