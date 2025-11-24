"""
ZenEnd Backend - Main Server
Chạy HTTP API và WebSocket trên CÙNG PORT (Render-compatible)
"""

import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from config.settings import HTTP_PORT, HTTP_HOST, API_KEY
from core import PortManager
from api.routes import setup_routes

port_manager = PortManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager - Không cần start WebSocket server riêng nữa
    Vì WebSocket sẽ chạy trực tiếp trên FastAPI
    """
    yield
    
    # Cleanup
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

# 🆕 CORS middleware cho WebSocket
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (hoặc chỉ định cụ thể)
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

# ✅ WebSocket endpoint trực tiếp trên FastAPI
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint cho ZenTab extension
    Chạy trên cùng port với HTTP API
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

# Setup HTTP routes
setup_routes(app, port_manager)


if __name__ == "__main__":
    import os
    
    # Detect production environment
    is_production = os.getenv("RENDER") is not None
    port = int(os.getenv("PORT", HTTP_PORT))
    
    print(f"\n{'='*80}")
    print(f"🚀 ZenEnd Backend Starting...")
    print(f"{'='*80}")
    print(f"Environment: {'Production (Render)' if is_production else 'Local Development'}")
    print(f"HTTP API: http://{HTTP_HOST}:{port}")
    print(f"WebSocket: {'wss' if is_production else 'ws'}://{HTTP_HOST if not is_production else 'your-app.onrender.com'}:{port}/ws")
    print(f"{'='*80}\n")
    
    uvicorn.run(
        "main:app",
        host=HTTP_HOST,
        port=port,
        log_level="info",
        reload=False if is_production else True,
        reload_dirs=None if is_production else ["./"]
    )