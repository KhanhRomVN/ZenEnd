"""
HTTP API routes
"""
import re
import asyncio
import time
import uuid
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header

from config.settings import REQUEST_TIMEOUT
from models import ChatCompletionRequest, TabStatus, TabState
from .dependencies import verify_api_key
import uuid
import time


router = APIRouter()


def setup_routes(app, port_manager):
    """Setup routes với port_manager dependency"""
    
    from fastapi.responses import JSONResponse
    
    @router.get("/v1/model/info")
    async def model_info(api_key: str = Depends(verify_api_key)):
        """
        Trả về thông tin model cho Cline extension
        """
        return {
            "id": "deepseek-chat",
            "object": "model",
            "created": 1234567890,
            "owned_by": "zenend",
            "permission": [],
            "root": "deepseek-chat",
            "parent": None,
            "description": "DeepSeek Chat via ZenTab extension"
        }

    @router.get("/v1/models")
    async def list_models(api_key: str = Depends(verify_api_key)):
        """
        Danh sách models (OpenAI compatible)
        """
        return {
            "object": "list",
            "data": [
                {
                    "id": "deepseek-chat",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "zenend"
                },
                {
                    "id": "deepseek-coder",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "zenend"
                }
            ]
        }

    @router.post("/v1/chat/completions")
    async def chat_completions(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key)
    ):
        from api.fake_response import is_fake_mode_enabled, create_fake_response
        
        if is_fake_mode_enabled():
            fake_response = create_fake_response(
                model=request.model, 
                messages=request.messages,
                stream=request.stream if hasattr(request, 'stream') else False
            )
            
            # 🆕 LOG: Fake Response
            print("\n" + "="*80)
            print("[API] 📤 FAKE RESPONSE TO CLINE:")
            print("="*80)
            print(json.dumps(fake_response, indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            # Xử lý streaming response
            if request.stream and fake_response.get("object") == "chat.completion.chunk":
                # Trả về streaming response
                from fastapi.responses import StreamingResponse
                async def generate():
                    yield f"data: {json.dumps(fake_response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/plain"
                )
            else:
                # Trả về non-streaming response
                from fastapi.responses import JSONResponse
                return JSONResponse(content=fake_response, status_code=200)
        
        SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-coder-v2"]
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model}' not supported. Available models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        conn_status = port_manager.get_connection_status()
        
        available_tabs = await port_manager.request_fresh_tabs()
        
        if not available_tabs:
            raise HTTPException(
                status_code=503,
                detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
            )

        free_tabs = [
            tab for tab in available_tabs 
            if tab.get('status') == 'free' and tab.get('canAccept', True)
        ]

        if not free_tabs:
            cooling_tabs = [
                tab for tab in available_tabs 
                if tab.get('status') == 'free' and not tab.get('canAccept', False)
            ]
            
            if cooling_tabs:
                for tab in cooling_tabs:
                    tab_id = tab['tabId']
                    cooling_time = tab.get('coolingDown', 0)
                    
                    await asyncio.sleep(2)
                    
                    refreshed_tabs = await port_manager.request_fresh_tabs()
                    refreshed_tab = next((t for t in refreshed_tabs if t['tabId'] == tab_id), None)
                    
                    if refreshed_tab and refreshed_tab.get('canAccept', False):
                        selected_tab = refreshed_tab
                        break

                else:
                    raise HTTPException(
                        status_code=503,
                        detail="All tabs are currently busy or cooling down. Please try again in a few seconds."
                    )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="No tabs available. Please open DeepSeek tabs in ZenTab extension first."
                )
        else:
            selected_tab = free_tabs[0]

        tab_id = selected_tab['tabId']
        container_name = selected_tab.get('containerName', 'Unknown')

        request_id = f"api-{uuid.uuid4().hex[:16]}"

        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")

        raw_content = user_messages[-1].content
        
        if isinstance(raw_content, list):
            text_parts = []
            for item in raw_content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        text_parts.append("[IMAGE - Not supported]")
            
            prompt = "\n\n".join(text_parts)
        else:
            prompt = raw_content

        tab_state = TabState(
            tab_id=tab_id,
            container_name=container_name,
            title=selected_tab.get('title', ''),
            url=selected_tab.get('url', '')
        )
        tab_state.mark_busy(request_id)
        port_manager.request_to_tab[request_id] = tab_id

        port_manager.temp_tab_states[tab_id] = tab_state
        
        ws_message = {
            "type": "sendPrompt",
            "tabId": tab_id,
            "prompt": prompt,
            "requestId": request_id
        }
        
        try:
            await port_manager.websocket.send(json.dumps(ws_message))
        except Exception as e:
            tab_state.mark_free()
            port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=f"Failed to send prompt: {str(e)}")
        
        try:
            response = await port_manager.wait_for_response(request_id, REQUEST_TIMEOUT)
            
            if "error" in response:
                error_msg = response["error"]
                if "cooling down" in error_msg.lower() or "not ready" in error_msg.lower():
                    raise HTTPException(
                        status_code=503,
                        detail=error_msg
                    )
                else:
                    raise HTTPException(status_code=500, detail=error_msg)
            
            validated_response = validate_openai_response(response)
            validated_response = ensure_cline_compatibility(validated_response, request)
            validated_response = validate_tool_calls_format(validated_response)
            validated_response = final_response_validation(validated_response)
            validated_response = ultimate_content_safety_check(validated_response)

            from fastapi.responses import JSONResponse
            
            # 🆕 LOG: API Response trước khi gửi tới Cline
            print("\n" + "="*80)
            print("[API] 📤 FINAL RESPONSE TO CLINE:")
            print("="*80)
            print(json.dumps(validated_response, indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            return JSONResponse(
                content=validated_response,
                status_code=200,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "x-request-id": validated_response.get("id", "unknown")
                }
            )
            
        except HTTPException as he:
            if he.status_code == 503:
                raise
            else:
                fallback_response = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "deepseek-chat",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I apologize, but I'm experiencing temporary technical difficulties. Please try your request again in a moment."
                        },
                        "finish_reason": "stop",
                        "logprobs": None
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    },
                    "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
                }
                
                # 🆕 LOG: Fallback response
                print("\n" + "="*80)
                print("[API] ⚠️ FALLBACK RESPONSE TO CLINE:")
                print("="*80)
                print(json.dumps(fallback_response, indent=2, ensure_ascii=False))
                print("="*80 + "\n")
                
                from fastapi.responses import JSONResponse
                return JSONResponse(content=fallback_response, status_code=200)
        except Exception as e:
            port_manager.cleanup_temp_tab_state(tab_id)
            port_manager.request_to_tab.pop(request_id, None)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            port_manager.cleanup_temp_tab_state(tab_id)
    
    app.include_router(router)

def validate_openai_response(response: dict) -> dict:
    if "choices" not in response or not response["choices"]:
        fallback_response = {
            "id": response.get("id", f"chatcmpl-{uuid.uuid4().hex[:16]}"),
            "object": "chat.completion",
            "created": response.get("created", int(time.time())),
            "model": response.get("model", "deepseek-chat"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "(Empty response)"
                },
                "finish_reason": "stop",
                "logprobs": None
            }],
            "usage": response.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
        }
        return fallback_response
    
    for i, choice in enumerate(response["choices"]):
        if "message" not in choice:
            choice["message"] = {
                "role": "assistant",
                "content": ""
            }
        
        if "logprobs" not in choice:
            choice["logprobs"] = None
        
        if "finish_reason" not in choice:
            choice["finish_reason"] = "stop"
        
        message = choice["message"]
        
        if "role" not in message:
            message["role"] = "assistant"
        
        has_tool_calls = "tool_calls" in message and message["tool_calls"] is not None and len(message["tool_calls"]) > 0
        has_content = message.get("content") is not None and message.get("content") != ""
        
        if has_tool_calls:
            choice["finish_reason"] = "tool_calls"
            message["content"] = ""
        else:
            if not has_content:
                message["content"] = "I understand. How can I assist you with your ZenTab project?"
                choice["finish_reason"] = "stop"
    
    if "id" not in response:
        response["id"] = f"chatcmpl-{uuid.uuid4().hex[:16]}"
    
    if "object" not in response:
        response["object"] = "chat.completion"
    
    if "created" not in response:
        response["created"] = int(time.time())
    
    if "model" not in response:
        response["model"] = "deepseek-chat"
    
    if "usage" not in response:
        response["usage"] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    
    return response

def ensure_cline_compatibility(response: dict, request: ChatCompletionRequest) -> dict:
    if "choices" not in response or not response["choices"]:
        return response
    
    has_tools_in_request = any(
        msg.role == "system" and "TOOL USE" in str(msg.content) 
        for msg in request.messages
    )
    
    if has_tools_in_request and response["choices"]:
        choice = response["choices"][0]
        if "message" in choice:
            message = choice["message"]
            has_tool_calls = "tool_calls" in message and message["tool_calls"]
            has_content = message.get("content") and message["content"].strip()
            
    for i, choice in enumerate(response["choices"]):
        if "message" not in choice:
            choice["message"] = {"role": "assistant", "content": ""}
        
        message = choice["message"]
        
        content = message.get("content")
        has_content = content is not None and content != ""
        has_tool_calls = "tool_calls" in message and message["tool_calls"] is not None and len(message["tool_calls"]) > 0
                
        if has_tool_calls:
            valid_tool_calls = []
            for tool in message["tool_calls"]:
                if not isinstance(tool, dict):
                    continue
                
                if "function" not in tool or not tool["function"]:
                    continue
                
                function = tool["function"]
                if "name" not in function or not function["name"]:
                    continue
                
                if "arguments" not in function:
                    continue
                
                if "id" not in tool or not tool["id"]:
                    tool["id"] = f"call_{uuid.uuid4().hex[:24]}"
                
                if "type" not in tool:
                    tool["type"] = "function"
                
                valid_tool_calls.append(tool)
            
            if valid_tool_calls:
                message["tool_calls"] = valid_tool_calls
                choice["finish_reason"] = "tool_calls"
                
                if not has_content:
                    message["content"] = ""
            else:
                if "tool_calls" in message:
                    del message["tool_calls"]
                
                if not has_content:
                    message["content"] = "I understand. How can I help you with your project?"
                
                choice["finish_reason"] = "stop"
        else:
            if not has_content:
                message["content"] = "I understand. Please let me know how I can assist you with your ZenTab project."
                choice["finish_reason"] = "stop"
        
        if "index" not in choice:
            choice["index"] = i
        
        if "finish_reason" not in choice:
            if has_tool_calls:
                choice["finish_reason"] = "tool_calls"
            else:
                choice["finish_reason"] = "stop"
        
        if "logprobs" not in choice:
            choice["logprobs"] = None
        
        if not has_content and not has_tool_calls:
            message["content"] = "I understand. Please let me know how I can assist you with your ZenTab project."
            choice["finish_reason"] = "stop"
        
        if isinstance(message.get("content"), list):
            message["content"] = " ".join(str(item) for item in message["content"])
        elif not isinstance(message.get("content"), str):
            message["content"] = str(message.get("content", ""))
    
    if "system_fingerprint" not in response:
        response["system_fingerprint"] = f"fp_{uuid.uuid4().hex[:8]}"
    
    return response

def final_response_validation(response: dict) -> dict:
    required_fields = ['id', 'object', 'created', 'model', 'choices']
    for field in required_fields:
        if field not in response:
            if field == 'id':
                response['id'] = f"chatcmpl-{uuid.uuid4().hex[:16]}"
            elif field == 'object':
                response['object'] = "chat.completion"
            elif field == 'created':
                response['created'] = int(time.time())
            elif field == 'model':
                response['model'] = "deepseek-chat"
            elif field == 'choices':
                response['choices'] = [create_minimal_choice()]
    
    if not isinstance(response.get('choices'), list):
        response['choices'] = [create_minimal_choice()]
    
    if not response['choices']:
        response['choices'] = [create_minimal_choice()]
    
    for i, choice in enumerate(response['choices']):
        if not isinstance(choice, dict):
            response['choices'][i] = create_minimal_choice()
            continue
            
        if 'message' not in choice or not isinstance(choice['message'], dict):
            choice['message'] = create_minimal_message()
        
        message = choice['message']
        
        if 'content' not in message or message['content'] is None:
            message['content'] = "I understand. How can I help you with your project?"
        
        if not isinstance(message['content'], str):
            message['content'] = str(message['content'])
        
        if not message['content'].strip():
            message['content'] = "I understand. How can I help you with your project?"
        
        if "tool_calls" in message and message["tool_calls"] is None:
            del message["tool_calls"]
        
        if 'role' not in message or not message['role']:
            message['role'] = 'assistant'
        
        if 'finish_reason' not in choice or not choice['finish_reason']:
            choice['finish_reason'] = 'stop'
        
        if 'logprobs' not in choice:
            choice['logprobs'] = None
    
    if 'system_fingerprint' not in response:
        response['system_fingerprint'] = f"fp_{uuid.uuid4().hex[:8]}"
    
    if 'usage' not in response or not isinstance(response['usage'], dict):
        response['usage'] = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
    
    return response

def ultimate_content_safety_check(response: dict) -> dict:
    if not isinstance(response, dict):
        return create_minimal_valid_response()
    
    if "choices" not in response or not isinstance(response["choices"], list):
        response["choices"] = []
    
    if not response["choices"]:
        response["choices"] = [create_minimal_choice()]
    
    for i, choice in enumerate(response["choices"]):
        if not isinstance(choice, dict):
            response["choices"][i] = create_minimal_choice()
            continue
        
        if "message" not in choice or not isinstance(choice["message"], dict):
            choice["message"] = create_minimal_message()
        
        message = choice["message"]
        
        if "content" not in message or message["content"] is None:
            message["content"] = "I understand. How can I help you with your project?"
        elif message["content"] == "":
            message["content"] = "I understand. How can I help you with your project?"
        
        if not isinstance(message["content"], str) or not message["content"].strip():
            message["content"] = "I understand. How can I help you with your project?"
        
        if "tool_calls" in message and message["tool_calls"] is None:
            del message["tool_calls"]
        
        if "role" not in message or not message["role"]:
            message["role"] = "assistant"
        
        if "finish_reason" not in choice or not choice["finish_reason"]:
            choice["finish_reason"] = "stop"
        
        if "logprobs" not in choice:
            choice["logprobs"] = None
    
    required_top_fields = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion", 
        "created": int(time.time()),
        "model": "deepseek-chat",
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }
    
    for field, default_value in required_top_fields.items():
        if field not in response or response[field] is None:
            response[field] = default_value
    
    if "usage" not in response or not isinstance(response["usage"], dict):
        response["usage"] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    
    return response

def create_minimal_valid_response() -> dict:
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [create_minimal_choice()],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:8]}"
    }

def create_minimal_choice() -> dict:
    return {
        "index": 0,
        "message": create_minimal_message(),
        "finish_reason": "stop",
        "logprobs": None
    }

def create_minimal_message() -> dict:
    return {
        "role": "assistant",
        "content": "I understand. How can I help you with your project?"
    }

def validate_tool_calls_format(response: dict) -> dict:
    if "choices" not in response:
        return response
        
    for choice_idx, choice in enumerate(response["choices"]):
        if "message" not in choice:
            continue
            
        message = choice["message"]
        if "tool_calls" not in message or not message["tool_calls"]:
            continue
            
        tool_calls = message["tool_calls"]
        
        for i, tool_call in enumerate(tool_calls):
            if "function" not in tool_call:
                tool_call["function"] = {}
            
            function = tool_call["function"]
            
            arguments = function.get('arguments')
            if arguments and not isinstance(arguments, str):
                try:
                    function['arguments'] = json.dumps(arguments, ensure_ascii=False)
                except Exception:
                    function['arguments'] = "{}"
            
            if arguments and isinstance(arguments, str):
                try:
                    json.loads(arguments)
                except json.JSONDecodeError:
                    if not arguments.startswith('{'):
                        function['arguments'] = json.dumps({"message": arguments})
    
    return response

def ensure_streaming_compatibility(response: dict, request: ChatCompletionRequest) -> dict:
    if "stream" in response:
        del response["stream"]
    
    if "choices" in response and hasattr(response["choices"], '__iter__') and not isinstance(response["choices"], list):
        response["choices"] = list(response["choices"])
    
    for i, choice in enumerate(response.get("choices", [])):
        if hasattr(choice, '__dict__'):
            response["choices"][i] = choice.__dict__
    
    return response

def validate_cline_specific_requirements(response: dict) -> dict:
    required_fields = ['id', 'object', 'created', 'model', 'choices', 'usage']
    
    for field in required_fields:
        if field not in response:
            if field == 'id':
                response['id'] = f"chatcmpl-{uuid.uuid4().hex[:16]}"
            elif field == 'object':
                response['object'] = "chat.completion"
            elif field == 'created':
                response['created'] = int(time.time())
            elif field == 'model':
                response['model'] = "deepseek-chat"
            elif field == 'choices':
                response['choices'] = [create_minimal_choice()]
            elif field == 'usage':
                response['usage'] = {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0
                }
    
    for i, choice in enumerate(response.get("choices", [])):
        if "index" not in choice:
            choice["index"] = i
        
        if "finish_reason" not in choice or not isinstance(choice["finish_reason"], str):
            choice["finish_reason"] = "stop"
        
        if "logprobs" not in choice:
            choice["logprobs"] = None
        
        if "message" not in choice or not isinstance(choice["message"], dict):
            choice["message"] = create_minimal_message()
        
        message = choice["message"]
        
        if "role" not in message or not isinstance(message["role"], str):
            message["role"] = "assistant"
        
        has_content = message.get("content") is not None and message["content"] != ""
        has_tool_calls = "tool_calls" in message and message["tool_calls"]
        
        if has_tool_calls and has_content:
            pass
        
        if not has_content and not has_tool_calls:
            message["content"] = "I understand. How can I help you with your project?"
            choice["finish_reason"] = "stop"
    
    return response

def ensure_cline_tool_compatibility(response: dict) -> dict:
    if "choices" not in response:
        return response
        
    for choice in response["choices"]:
        if "message" not in choice:
            continue
            
        message = choice["message"]
        if "tool_calls" not in message or not message["tool_calls"]:
            continue
            
        tool_calls = message["tool_calls"]
        valid_tools = []
        
        for tool in tool_calls:
            tool_name = tool.get('function', {}).get('name', '')
            
            cline_tools = {
                'task_progress', 'read_file', 'write_to_file', 'replace_in_file',
                'search_files', 'list_files', 'execute_command', 'ask_followup_question',
                'attempt_completion', 'use_mcp_tool', 'access_mcp_resource'
            }
            
            if tool_name in cline_tools:
                valid_tools.append(tool)
        
        message["tool_calls"] = valid_tools
        
        if not valid_tools:
            message.pop("tool_calls", None)
            choice["finish_reason"] = "stop"
    
    return response