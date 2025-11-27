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
    """
    Handle Pydantic validation errors
    🔥 CRITICAL: Log chi tiết và trả về error response thân thiện
    """
    from core import error as log_error
    
    errors = exc.errors()
    
    # Log validation error
    log_error(
        "Request validation failed",
        {
            "path": request.url.path,
            "method": request.method,
            "error_count": len(errors),
            "errors": str(errors)[:200]  # Truncate for log
        },
        show_traceback=False
    )
    
    # Return user-friendly error
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "message": "Yêu cầu không hợp lệ - kiểm tra lại format của request body",
            "hint": "Đảm bảo các field bắt buộc (model, messages) có mặt và đúng type"
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """
    Handle tất cả các exception chưa được xử lý
    🔥 CRITICAL: Last line of defense - log mọi exception
    """
    from core import critical as log_critical
    import traceback
    
    # Log exception với full traceback
    tb = traceback.format_exc()
    log_critical(
        f"Unhandled exception: {str(exc)}",
        {
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": tb[:500]  # Truncate for metadata
        },
        show_traceback=True
    )
    
    # Return generic error response
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_server_error",
                "code": "internal_error",
                "hint": "Lỗi máy chủ nội bộ. Vui lòng kiểm tra log để biết chi tiết."
            }
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    from websocket.handlers import handle_fastapi_websocket_connection
    
    await websocket.accept()
    
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
    
    uvicorn.run(
        "main:app",
        host=HTTP_HOST,
        port=port,
        log_level="info",
        reload=False if is_production else True,
        reload_dirs=None if is_production else ["./"]
    )