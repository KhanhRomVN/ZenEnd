# ZenEnd 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Ready-brightgreen.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

> High-performance backend server that bridges ZenTab browser extension with Cline AI coding assistant. Provides OpenAI-compatible API with intelligent tab routing and real-time WebSocket communication.

![ZenEnd Architecture](https://via.placeholder.com/1200x400/2c3e50/ecf0f1?text=ZenEnd+-+AI+Backend+Bridge)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**ZenEnd** is a FastAPI-based backend server that acts as a bridge between:
- **ZenTab Extension**: Manages DeepSeek AI tabs in browser
- **Cline Extension**: AI coding assistant in VS Code

It provides an **OpenAI-compatible API** that routes requests to available DeepSeek tabs via WebSocket, enabling seamless AI-powered coding workflows.

### Why ZenEnd?

- **OpenAI-Compatible**: Drop-in replacement for OpenAI API endpoints
- **Smart Routing**: Automatically selects free tabs based on folder context
- **Real-Time Sync**: WebSocket communication for low-latency responses
- **Production-Ready**: Built with FastAPI, async-first, deployment-ready
- **Render Compatible**: Single-port design for easy cloud deployment

---

## ✨ Key Features

### 🔌 OpenAI-Compatible API
- **Chat Completions**: `/v1/chat/completions` endpoint
- **Model Info**: `/v1/models` and `/v1/model/info` endpoints
- **Streaming Support**: Server-Sent Events (SSE) format
- **Error Handling**: Comprehensive error responses with retry logic

### 🎯 Intelligent Tab Routing
- **New Task Detection**: Identifies `<task>` tags for fresh tab allocation
- **Folder-Based Routing**: Routes to tabs linked with specific project folders
- **Availability Checking**: Real-time tab status validation (free/busy/sleep)
- **Auto-Recovery**: Detects and recovers from timeout/error states

### 🌐 WebSocket Management
- **Single Connection**: Efficient single WebSocket connection
- **Health Monitoring**: Ping/pong with 45-second intervals
- **Message Deduplication**: Prevents duplicate request processing
- **Request Cleanup**: Automatic cleanup of stale requests

### 📝 Advanced Logging
- **Colored Console Logs**: Level-based color coding (DEBUG/INFO/WARNING/ERROR)
- **Request/Response Logging**: Full request/response capture
- **Image Extraction**: Saves base64 images from requests
- **System Prompt Logging**: Tracks AI system prompts

### 🛡️ Production Features
- **CORS Support**: Configurable cross-origin requests
- **API Key Authentication**: Bearer token validation
- **Health Checks**: `/health` endpoint for monitoring
- **Graceful Shutdown**: Proper cleanup on server stop

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Cline Extension (VS Code)                  │
│                  OpenAI-Compatible Client                     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP POST /v1/chat/completions
                         │ Authorization: Bearer API_KEY
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      ZenEnd Backend                           │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   FastAPI    │◄────►│  WebSocket   │◄────►│   Port     │ │
│  │   Routes     │      │   Handler    │      │  Manager   │ │
│  └──────────────┘      └──────────────┘      └────────────┘ │
│         │                      │                     │        │
│         │                      │                     │        │
│         ▼                      ▼                     ▼        │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   Request    │      │   Message    │      │  Response  │ │
│  │   Parser     │      │   Processor  │      │   Parser   │ │
│  └──────────────┘      └──────────────┘      └────────────┘ │
│                                                                │
└────────────────────────────┬───────────────────────────────────┘
                             │ WebSocket (ws:// or wss://)
                             │ {"type": "sendPrompt", ...}
                             ▼
                ┌────────────────────────────────┐
                │     ZenTab Extension           │
                │  (Browser - DeepSeek Tabs)     │
                └────────────────────────────────┘
```

### Request Flow

1. **Cline** sends HTTP POST to `/v1/chat/completions`
2. **ZenEnd** validates API key and parses request
3. **Tab Selection**:
   - New task? → Request fresh available tabs
   - Existing task? → Find tabs linked to folder
4. **WebSocket Send**: Forward prompt to selected tab
5. **Wait for Response**: Poll for response with timeout
6. **Response Parsing**: Convert DeepSeek → OpenAI format
7. **Stream Back**: Send SSE stream to Cline

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip or poetry
- Running ZenTab extension (for WebSocket connection)

### Installation

```bash
# Clone repository
git clone https://github.com/KhanhRomVN/ZenEnd.git
cd ZenEnd

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
# Set API key (optional - default: "re")
export API_KEY="your-secret-key"

# Start server
python main.py

# Server runs on http://localhost:3030
```

### Test Connection

```bash
# Health check
curl http://localhost:3030/health

# List models
curl -H "Authorization: Bearer THIS_IS_API_KEY" \
     http://localhost:3030/v1/models
```

---

## 📚 API Documentation

### Authentication

All endpoints require API key in header:
```
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### 1. Chat Completions
**POST** `/v1/chat/completions`

OpenAI-compatible chat completion endpoint.

**Request:**
```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful coding assistant..."
    },
    {
      "role": "user",
      "content": "Write a Python function to calculate factorial"
    }
  ],
  "temperature": 0.7,
  "stream": false
}
```

**Response (Streaming):**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk",...}

data: [DONE]
```

#### 2. List Models
**GET** `/v1/models`

Returns available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "deepseek-chat",
      "object": "model",
      "created": 1234567890,
      "owned_by": "zenend"
    }
  ]
}
```

#### 3. Model Info
**GET** `/v1/model/info`

Returns specific model information.

**Response:**
```json
{
  "id": "deepseek-chat",
  "object": "model",
  "description": "DeepSeek Chat via ZenTab extension"
}
```

#### 4. Health Check
**GET** `/health`

Server health status (no auth required).

**Response:**
```json
{
  "status": "healthy",
  "service": "ZenEnd Backend",
  "version": "1.0.0",
  "timestamp": 1234567890,
  "websocket_enabled": true
}
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# API Key for authentication
API_KEY=your-secret-key-here

# Server port (default: 3030)
PORT=3030

# Request timeout in seconds (default: 180)
REQUEST_TIMEOUT=180

# Enable fake mode (testing without ZenTab)
ENABLE_FAKE_RESPONSE=false
```

### Settings File

Edit `config/settings.py`:

```python
# API Authentication
API_KEY = os.getenv("API_KEY", "THIS_IS_API_KEY")

# Server Configuration
HTTP_PORT = int(os.getenv("PORT", 3030))
HTTP_HOST = "0.0.0.0"

# Request Timeout
REQUEST_TIMEOUT = 180  # 3 minutes
```

---

## 🌐 Deployment

### Render.com (Recommended)

ZenEnd is optimized for Render deployment with single-port design.

**render.yaml:**
```yaml
services:
  - type: web
    name: zenend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: API_KEY
        generateValue: true
      - key: PORT
        value: 10000
```

**Deploy:**
```bash
# Connect GitHub repo to Render
# Push to main branch
git push origin main

# Render auto-deploys
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3030
CMD ["python", "main.py"]
```

**Run:**
```bash
docker build -t zenend .
docker run -p 3030:3030 -e API_KEY=secret zenend
```

### Manual VPS

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 3030

# Or with systemd service
sudo systemctl enable zenend
sudo systemctl start zenend
```

---

## 🛠️ Development

### Project Structure

```
ZenEnd/
├── main.py                  # Application entry point
├── api/
│   ├── routes.py            # API route handlers
│   ├── dependencies.py      # Auth & dependencies
│   └── middleware.py        # Request logging
├── core/
│   ├── port_manager.py      # WebSocket & tab management
│   ├── logger.py            # Colored logging
│   ├── response_parser.py   # Response format conversion
│   └── fake_response.py     # Testing without ZenTab
├── models/
│   ├── requests.py          # Request models
│   └── enums.py             # Status enums
├── websocket/
│   └── handlers.py          # WebSocket message handlers
├── config/
│   └── settings.py          # Configuration
└── requirements.txt
```

### Key Components

#### 1. **PortManager** (`core/port_manager.py`)
Manages WebSocket connection and request routing.

```python
port_manager = PortManager()

# Request available tabs
tabs = await port_manager.request_fresh_tabs(timeout=10.0)

# Request tabs by folder
tabs = await port_manager.request_tabs_by_folder("/path/to/project")

# Wait for response
response = await port_manager.wait_for_response(request_id, timeout=180.0)
```

#### 2. **Logger** (`core/logger.py`)
Colored console logging with metadata.

```python
from core import info, error, error_response

info("Server started", {"port": 3030})
error("WebSocket failed", {"retry": 3}, show_traceback=True)

# Return error response to client
return error_response(
    error_message="Tab not available",
    detail_message="No free tabs found",
    status_code=503
)
```

#### 3. **Message Handlers** (`websocket/handlers.py`)
Process incoming WebSocket messages.

```python
# Handle message types
- "availableTabs": Tab list response
- "promptResponse": AI response from DeepSeek
- "focusedTabsUpdate": Tab status update
```

### Running Tests

```bash
# Enable fake mode for testing without ZenTab
export ENABLE_FAKE_RESPONSE=true

# Run server
python main.py

# Test endpoint
curl -X POST http://localhost:3030/v1/chat/completions \
  -H "Authorization: Bearer THIS_IS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Debug Mode

Enable detailed logging:

```python
# In core/logger.py
ENABLE_LOGGING = True  # Set False to disable logs

# In api/middleware.py
# Middleware logs:
# - Full request body
# - System prompts
# - Base64 images (saved to logs/images/)
```

---

## 🐛 Troubleshooting

### WebSocket Connection Issues

**Problem:** `WebSocket not connected` error

**Solutions:**
1. Ensure ZenTab extension is running
2. Check WebSocket URL in extension settings
3. Verify no firewall blocking port 3030
4. Check browser console for WebSocket errors

### Tab Not Available

**Problem:** `No available tabs` error

**Solutions:**
1. Open at least one DeepSeek tab in browser
2. Check tab status in ZenTab sidebar (should show "free")
3. Wait for any busy tabs to complete
4. Force reset stuck tabs in ZenTab sidebar

### Request Timeout

**Problem:** `Request timeout after 180s`

**Solutions:**
1. Increase `REQUEST_TIMEOUT` in settings
2. Check if DeepSeek is responding in browser
3. Verify tab is not stuck in "busy" state
4. Check network connection to DeepSeek

### Response Parsing Errors

**Problem:** `Invalid response format` error

**Solutions:**
1. Check if DeepSeek UI has changed
2. Enable debug logging to see raw response
3. Check for network issues corrupting response
4. Verify ZenTab extension is up-to-date

### Deployment Issues

**Problem:** Health check failing on Render

**Solutions:**
1. Ensure `PORT` env var is set correctly
2. Check Render logs for startup errors
3. Verify `requirements.txt` has all dependencies
4. Test locally with same env vars

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 KhanhRomVN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📧 Contact

**Khánh Rom**
- GitHub: [@KhanhRomVN](https://github.com/KhanhRomVN)
- Email: khanhromvn@gmail.com

**Project Link:** [https://github.com/KhanhRomVN/ZenEnd](https://github.com/KhanhRomVN/ZenEnd)

**Related Projects:**
- [ZenTab Extension](https://github.com/KhanhRomVN/ZenTab) - Browser extension for DeepSeek tab management

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Starlette](https://www.starlette.io/) - ASGI toolkit
- [DeepSeek](https://www.deepseek.com/) - AI platform

---

<div align="center">

Made with ❤️ by [KhanhRomVN](https://github.com/KhanhRomVN)

⭐ Star this repo if you find it helpful!

**Architecture:** ZenEnd ↔ ZenTab ↔ DeepSeek

</div>