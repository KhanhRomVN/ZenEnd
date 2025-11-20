``` trường hợp dùng fake response
[WebSocket] New connection established from ('127.0.0.1', 34378)
INFO:     127.0.0.1:37078 - "GET /v1/model/info HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:37092 - "GET /v1/model/info HTTP/1.1" 200 OK
[FakeResponse] 📊 Created streaming chunk response:
[FakeResponse]   - object: chat.completion.chunk
[FakeResponse]   - has delta: True
[FakeResponse]   - content length: 532
[API] 📨 FAKE RESPONSE generated - requestId: 3c447299a4df464d
[API] 📊 Fake response type: <class 'dict'>
[API] 📊 Fake response keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[API] 📝 RAW FAKE RESPONSE (no truncate):
{
  "id": "chatcmpl-38994d79174a4b3a",
  "object": "chat.completion.chunk",
  "created": 1763637101,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "I can see you're in PLAN MODE and you've sent a simple \"hello\" task. Since this is a straightforward greeting, I don't need extensive planning. I'm ready to help you with the ZenEnd backend project. \n\nThe project structure looks well-organized with API routes, WebSocket handlers, and core management components. I can assist with exploring the codebase, implementing features, or debugging issues.\n\nWould you like me to switch to ACT MODE to start working on specific tasks, or do you have a particular planning discussion in mind?"
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 133,
    "total_tokens": 418
  },
  "system_fingerprint": "fp_ecbe3dee"
}
[API] ═══════════════════════════════════════
[API] 🔍 FAKE RESPONSE STRUCTURE DETAILS:
[API]   - response keys: ['choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage']
[API]   - choice keys: ['delta', 'finish_reason', 'index', 'logprobs']
[API]   - message keys: []
[API]   - message.content type: NoneType
[API]   - message.content is None: True
[API]   - message.tool_calls: None
[API] ═══════════════════════════════════════
INFO:     127.0.0.1:37078 - "POST /v1/chat/completions HTTP/1.1" 200 OK
[FakeResponse] 📊 Created streaming chunk response:
[FakeResponse]   - object: chat.completion.chunk
[FakeResponse]   - has delta: True
[FakeResponse]   - content length: 532
[API] 📨 FAKE RESPONSE generated - requestId: 295d143db9bf409f
[API] 📊 Fake response type: <class 'dict'>
[API] 📊 Fake response keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[API] 📝 RAW FAKE RESPONSE (no truncate):
{
  "id": "chatcmpl-18d7c6d2ee334f6f",
  "object": "chat.completion.chunk",
  "created": 1763637101,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "I can see you're in PLAN MODE and you've sent a simple \"hello\" task. Since this is a straightforward greeting, I don't need extensive planning. I'm ready to help you with the ZenEnd backend project. \n\nThe project structure looks well-organized with API routes, WebSocket handlers, and core management components. I can assist with exploring the codebase, implementing features, or debugging issues.\n\nWould you like me to switch to ACT MODE to start working on specific tasks, or do you have a particular planning discussion in mind?"
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 133,
    "total_tokens": 418
  },
  "system_fingerprint": "fp_18b7446c"
}
[API] ═══════════════════════════════════════
[API] 🔍 FAKE RESPONSE STRUCTURE DETAILS:
[API]   - response keys: ['choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage']
[API]   - choice keys: ['delta', 'finish_reason', 'index', 'logprobs']
[API]   - message keys: []
[API]   - message.content type: NoneType
[API]   - message.content is None: True
[API]   - message.tool_calls: None
[API] ═══════════════════════════════════════
INFO:     127.0.0.1:37078 - "POST /v1/chat/completions HTTP/1.1" 200 OK
[FakeResponse] 📊 Created streaming chunk response:
[FakeResponse]   - object: chat.completion.chunk
[FakeResponse]   - has delta: True
[FakeResponse]   - content length: 532
[API] 📨 FAKE RESPONSE generated - requestId: ff5a91a620ef4b28
[API] 📊 Fake response type: <class 'dict'>
[API] 📊 Fake response keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[API] 📝 RAW FAKE RESPONSE (no truncate):
{
  "id": "chatcmpl-199aecf829694da4",
  "object": "chat.completion.chunk",
  "created": 1763637101,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "I can see you're in PLAN MODE and you've sent a simple \"hello\" task. Since this is a straightforward greeting, I don't need extensive planning. I'm ready to help you with the ZenEnd backend project. \n\nThe project structure looks well-organized with API routes, WebSocket handlers, and core management components. I can assist with exploring the codebase, implementing features, or debugging issues.\n\nWould you like me to switch to ACT MODE to start working on specific tasks, or do you have a particular planning discussion in mind?"
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 133,
    "total_tokens": 418
  },
  "system_fingerprint": "fp_57c16f50"
}
[API] ═══════════════════════════════════════
[API] 🔍 FAKE RESPONSE STRUCTURE DETAILS:
[API]   - response keys: ['choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage']
[API]   - choice keys: ['delta', 'finish_reason', 'index', 'logprobs']
[API]   - message keys: []
[API]   - message.content type: NoneType
[API]   - message.content is None: True
[API]   - message.tool_calls: None
[API] ═══════════════════════════════════════
INFO:     127.0.0.1:37078 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

``` trường hợp dùng real response
[WebSocket] New connection established from ('127.0.0.1', 48168)
INFO:     127.0.0.1:48902 - "GET /v1/model/info HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:48908 - "GET /v1/model/info HTTP/1.1" 200 OK
[API] Connection status: {'websocket_connected': True, 'websocket_open': True, 'port': 1500, 'connection_age': 17.813076734542847}
[API] ✅ WebSocket connected, requesting fresh tabs...
[PortManager] request_fresh_tabs() called with timeout=10.0s
[PortManager] Generated request_id: tabs_req_5536c0e3
[PortManager] Sending getAvailableTabs request to ZenTab: {'type': 'getAvailableTabs', 'requestId': 'tabs_req_5536c0e3', 'timestamp': 1763636999948, 'urgent': True}
[PortManager] ✅ Request sent, waiting for response (timeout=10.0s)...
[WebSocket] Received availableTabs response - request_id: tabs_req_5536c0e3, tabs count: 1
[WebSocket]   Tab 0: tabId=2, status=free, canAccept=True
[WebSocket] Resolving future for request_id: tabs_req_5536c0e3
[PortManager] handle_available_tabs_response() called - request_id: tabs_req_5536c0e3, tabs: 1
[PortManager] ✅ Setting result for request_id: tabs_req_5536c0e3
[WebSocket] Received availableTabs response - request_id: tabs_req_5536c0e3, tabs count: 1
[WebSocket] ⚠️ Future already done for request_id: tabs_req_5536c0e3, ignoring duplicate response
[PortManager] ✅ Received response with 1 tabs
[PortManager] Cleaned up request_id: tabs_req_5536c0e3
[API] Received 1 tabs from ZenTab
[API] Selected tab: {'tabId': 2, 'containerName': 'Tab 2', 'title': 'DeepSeek - Into the Unknown', 'url': 'https://chat.deepseek.com/', 'status': 'free', 'canAccept': True, 'requestCount': 0}
[API] Tab status: free, canAccept: True
[WebSocket] 📨 RAW RESPONSE from ZenTab - requestId: api-e2507e6e376c4278
[WebSocket] 📊 Response type: <class 'dict'>
[WebSocket] 📝 Response length: 1267
[WebSocket] 📄 RAW RESPONSE CONTENT (no truncate):
{'id': 'chatcmpl-8a3b5c7d9e1f2a3b', 'object': 'chat.completion.chunk', 'created': 1763637002, 'model': 'deepseek-chat', 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."}, 'finish_reason': 'stop', 'logprobs': None}], 'usage': {'prompt_tokens': 285, 'completion_tokens': 175, 'total_tokens': 460}, 'system_fingerprint': 'fp_4c8d9e2f'}
[WebSocket] ═══════════════════════════════════════
[WebSocket] ✅ Response is already a dict, using directly
[WebSocket] 📊 PARSED RESPONSE STRUCTURE (before ensure_openai_format):
[WebSocket]   - Type: <class 'dict'>
[WebSocket]   - Keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[WebSocket]   - Has 'id': True
[WebSocket]   - Has 'object': True
[WebSocket]   - Has 'choices': True
[WebSocket]   - Choices count: 1
[WebSocket]   - First choice keys: ['index', 'delta', 'finish_reason', 'logprobs']
[WebSocket]   - Has 'message': False
[WebSocket]   - Has 'delta': True
[WebSocket] 📝 FULL PARSED RESPONSE (no truncate):
{
  "id": "chatcmpl-8a3b5c7d9e1f2a3b",
  "object": "chat.completion.chunk",
  "created": 1763637002,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 175,
    "total_tokens": 460
  },
  "system_fingerprint": "fp_4c8d9e2f"
}
[WebSocket] ═══════════════════════════════════════
[WebSocket] 🎯 FINAL RESPONSE (after ensure_openai_format) - requestId: api-e2507e6e376c4278
[WebSocket] 📊 Final response type: <class 'dict'>
[WebSocket] 📊 Final response keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[WebSocket]   - object: chat.completion
[WebSocket]   - model: deepseek-chat
[WebSocket]   - choices count: 1
[WebSocket]   - First choice finish_reason: stop
[WebSocket]   - Message role: assistant
[WebSocket]   - Message content type: <class 'str'>
[WebSocket]   - Message content length: 899
[WebSocket]   - Has tool_calls: False
[WebSocket] 📝 COMPLETE FINAL RESPONSE (no truncate):
{
  "id": "chatcmpl-8a3b5c7d9e1f2a3b",
  "object": "chat.completion",
  "created": 1763637002,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "logprobs": null,
      "message": {
        "role": "assistant",
        "content": "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 175,
    "total_tokens": 460
  },
  "system_fingerprint": "fp_4c8d9e2f"
}
[WebSocket] ═══════════════════════════════════════
[API] 📨 RECEIVED RESPONSE from PortManager - requestId: api-e2507e6e376c4278
[API] 📊 Response type: <class 'dict'>
[API] 📊 Response keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[API] 📝 COMPLETE RESPONSE (no truncate):
{
  "id": "chatcmpl-8a3b5c7d9e1f2a3b",
  "object": "chat.completion",
  "created": 1763637002,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "logprobs": null,
      "message": {
        "role": "assistant",
        "content": "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 175,
    "total_tokens": 460
  },
  "system_fingerprint": "fp_4c8d9e2f"
}
[API] ═══════════════════════════════════════
[API] 🔍 REAL RESPONSE STRUCTURE DETAILS (BEFORE VALIDATION):
[API]   - response keys: ['choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage']
[API]   - choice keys: ['finish_reason', 'index', 'logprobs', 'message']
[API]   - message keys: ['content', 'role']
[API]   - message.content type: str
[API]   - message.content is None: False
[API]   - message.tool_calls: None
[API]   - Has 'delta' in choice: False
[API]   - object type: chat.completion
[API] ═══════════════════════════════════════
[API] 🔍 VALIDATING RESPONSE STRUCTURE...
[API]   - Has 'id': True
[API]   - Has 'object': True
[API]   - Has 'created': True
[API]   - Has 'model': True
[API]   - Has 'choices': True
[API] 📊 First choice structure:
[API]   - Choice keys: ['index', 'finish_reason', 'logprobs', 'message']
[API]   - finish_reason: stop
[API]   - Message keys: ['role', 'content']
[API]   - Message role: assistant
[API]   - Message content type: <class 'str'>
[API]   - Message has tool_calls: False
[API]   - Content length: 899
[API]   - Content preview (first 200 chars): Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which 
[API] ✅ Response structure validation completed
[API] 📨 REAL RESPONSE received from PortManager - requestId: api-e2507e6e376c4278
[API] 📊 Real response type: <class 'dict'>
[API] 📝 RAW REAL RESPONSE (before validation):
{
  "id": "chatcmpl-8a3b5c7d9e1f2a3b",
  "object": "chat.completion",
  "created": 1763637002,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "logprobs": null,
      "message": {
        "role": "assistant",
        "content": "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 175,
    "total_tokens": 460
  },
  "system_fingerprint": "fp_4c8d9e2f"
}
[API] ═══════════════════════════════════════
[API-VALIDATE] 🔍 Validating REAL response - requestId: api-e2507e6e376c4278
[API-VALIDATE] 📊 Input type: <class 'dict'>
[API-VALIDATE] 📊 Input keys: ['id', 'object', 'created', 'model', 'choices', 'usage', 'system_fingerprint']
[API-VALIDATE] 📊 Object type: chat.completion
[API-VALIDATE] 📊 First choice keys: ['index', 'finish_reason', 'logprobs', 'message']
[API-VALIDATE] 📊 Message keys: ['role', 'content']
[API-VALIDATE] 📊 Message role: assistant
[API-VALIDATE] 📊 Message has content: True
[API-VALIDATE] 📊 Content type: <class 'str'>
[API-VALIDATE] 📊 Content length: 899
[API-VALIDATE] 📝 Content preview (first 200 chars): Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which 
[API-VALIDATE] ✅ Response validation completed successfully
[API-VALIDATE] 📝 Final response summary:
[API-VALIDATE]   - object: chat.completion
[API-VALIDATE]   - model: deepseek-chat
[API-VALIDATE]   - finish_reason: stop
[API-VALIDATE]   - message.role: assistant
[API-VALIDATE]   - message.content length: 899
[API-VALIDATE]   - has tool_calls: False
[API-VALIDATE] 🔍 DEEP STRUCTURE ANALYSIS (REAL):
[API-VALIDATE]   - response type: dict
[API-VALIDATE]   - choices type: list
[API-VALIDATE]   - first choice type: dict
[API-VALIDATE]   - message type: dict
[API-VALIDATE]   - content type: str
[API-VALIDATE]   - All response keys: ['choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage']
[API-VALIDATE]   - All choice keys: ['finish_reason', 'index', 'logprobs', 'message']
[API-VALIDATE]   - All message keys: ['content', 'role']
[API] 🚀 SENDING REAL RESPONSE TO CLINE (after validation) - requestId: api-e2507e6e376c4278
[API] 📊 Final response type: <class 'dict'>
[API] 📝 COMPLETE FINAL RESPONSE TO CLINE (no truncate):
{
  "id": "chatcmpl-8a3b5c7d9e1f2a3b",
  "object": "chat.completion",
  "created": 1763637002,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "logprobs": null,
      "message": {
        "role": "assistant",
        "content": "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket functionality, background scripts, and a React-based sidebar interface. You're currently in PLAN MODE, which is perfect for discussing approaches and creating implementation strategies.\\n\\nLooking at your project structure, I can see you have:\\n- Background scripts for WebSocket management and deepseek integration\\n- React components for the sidebar UI\\n- Content scripts and various utilities\\n- A well-organized TypeScript codebase\\n\\nWhat would you like to work on today? I can help you plan:\\n- New feature implementations\\n- Code refactoring or improvements\\n- Bug fixes or debugging\\n- Architecture decisions\\n- Integration with external services\\n\\nCould you share what specific task or challenge you'd like to tackle? This will help me understand your goals and create a comprehensive plan for you."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 285,
    "completion_tokens": 175,
    "total_tokens": 460
  },
  "system_fingerprint": "fp_4c8d9e2f"
}
[API] 🔍 FINAL REAL STRUCTURE CHECK (AFTER VALIDATION):
[API]   - Has 'choices'[0]['message']: True
[API]   - message keys: ['role', 'content']
[API]   - message['content'] exists: True
[API]   - message['role'] exists: True
[API]   - message['content'] type: str
[API]   - message['content'] value: "Hello! I can see you're working on the ZenTab project - a browser extension with WebSocket function
[API]   - Extra keys in message: set()
[API]   - object type: chat.completion
[API]   - finish_reason: stop
[API] 📊 COMPARISON CHECK:
[API]   - Real response has same keys as fake? (checking structure similarity)
[API]   - Real message keys: ['content', 'role']
[API]   - Expected message keys: ['content', 'role'] or ['content', 'role', 'tool_calls']
[API] ═══════════════════════════════════════
INFO:     127.0.0.1:48902 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

nhưng với real response thì Cline có lỗi này
```
{"message":"Cannot read properties of undefined (reading 'type')","modelId":"deepseek-chat"}
```