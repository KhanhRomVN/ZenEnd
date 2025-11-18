"""
ZenEnd Backend - Main Server
Chạy 10 WebSocket servers (1501-1510) và HTTP API để bridge với ZenTab
"""

import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from config.settings import WS_PORT, HTTP_PORT, HTTP_HOST, API_KEY
from core import PortManager
from api.routes import setup_routes
from websocket import start_websocket_server
from api.response_logger import ResponseLoggerMiddleware

port_manager = PortManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    ws_task = asyncio.create_task(start_websocket_server(WS_PORT, port_manager))
    
    yield
    ws_task.cancel()


app = FastAPI(
    title="ZenEnd",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ResponseLoggerMiddleware)

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

setup_routes(app, port_manager)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level="info",
        reload=True,
        reload_dirs=["./"]
    )