"""
ZenEnd Backend - Main Server
Chạy 10 WebSocket servers (1501-1510) và HTTP API để bridge với ZenTab
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from config.settings import WS_PORTS, HTTP_PORT, HTTP_HOST, API_KEY
from core import PortManager
from api.routes import setup_routes
from websocket import start_websocket_server


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================
port_manager = PortManager()


# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    # Startup: Khởi động WebSocket servers
    ws_tasks = []
    for port in WS_PORTS:
        task = asyncio.create_task(start_websocket_server(port, port_manager))
        ws_tasks.append(task)
    
    yield
    
    # Shutdown: Cancel WebSocket tasks
    for task in ws_tasks:
        task.cancel()


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