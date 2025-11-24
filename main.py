"""
ZenEnd Backend - Main Server
Chạy HTTP API và WebSocket trên CÙNG PORT (Render-compatible)
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from config.settings import HTTP_PORT, HTTP_HOST
from core import PortManager
from api.routes import setup_routes

port_manager = PortManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager - chỉ cleanup khi shutdown
    """
    yield
    
    if port_manager.websocket:
        try:
            await port_manager.websocket.close()
        except:
            pass


app = FastAPI(
    title="ZenEnd",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.middleware import DebugRequestMiddleware
app.add_middleware(DebugRequestMiddleware)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "message": "Validation failed - check request format"
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_server_error",
                "code": "internal_error"
            }
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint cho ZenTab extension
    CHỈ hoạt động khi có client kết nối (local development)
    """
    from websocket.handlers import handle_fastapi_websocket_connection
    
    await websocket.accept()
    print(f"[WebSocket] ✅ Client connected from {websocket.client.host}:{websocket.client.port}")
    
    try:
        await handle_fastapi_websocket_connection(websocket, port_manager)
    except WebSocketDisconnect:
        print(f"[WebSocket] ❌ Client disconnected")
    except Exception as e:
        print(f"[WebSocket] ❌ Error: {e}")
    finally:
        if port_manager.websocket == websocket:
            port_manager.websocket = None

setup_routes(app, port_manager)


if __name__ == "__main__":
    is_production = os.getenv("RENDER") is not None
    port = int(os.getenv("PORT", HTTP_PORT))
    
    print(f"\n{'='*80}")
    print(f"🚀 ZenEnd Backend Starting...")
    print(f"{'='*80}")
    print(f"Environment: {'Production (Render)' if is_production else 'Local Development'}")
    print(f"HTTP API: http://{HTTP_HOST}:{port}")
    print(f"WebSocket: ws://{HTTP_HOST}:{port}/ws")
    print(f"    → ZenTab extension connects here (both prod & dev)")
    print(f"{'='*80}\n")
    
    uvicorn.run(
        "main:app",
        host=HTTP_HOST,
        port=port,
        log_level="info",
        reload=False if is_production else True,
        reload_dirs=None if is_production else ["./"]
    )