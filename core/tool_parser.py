"""
Parse tool calls từ DeepSeek response và convert sang OpenAI format
"""
import re
import json
import uuid
from typing import Dict, List, Tuple, Optional


def parse_json_tools(content: str) -> Tuple[str, List[Dict]]:
    """
    Parse JSON tool calls từ content (Cline format)
    """
    if not content or not isinstance(content, str):
        return content, []
    
    tool_calls = []
    remaining_text = content
    
    patterns = [
        r'\{\s*"name"\s*:\s*"[^"]*"\s*,\s*"arguments"\s*:\s*\{[^{}]*\}\s*\}',
        r'{\s*"function"\s*:\s*{[^}]*}\s*}',
        r'function_call\s*:\s*\{[^}]+\}',
    ]
    
    for pattern in patterns:
        try:
            matches = list(re.finditer(pattern, content, re.DOTALL))
            
            for match in matches:
                try:
                    tool_data = json.loads(match.group(0))
                    
                    if isinstance(tool_data, dict):
                        tool_name = None
                        tool_args = None
                        
                        if "name" in tool_data and "arguments" in tool_data:
                            tool_name = tool_data["name"]
                            tool_args = tool_data["arguments"]
                        
                        elif "function" in tool_data and isinstance(tool_data["function"], dict):
                            if "name" in tool_data["function"] and "arguments" in tool_data["function"]:
                                tool_name = tool_data["function"]["name"]
                                tool_args = tool_data["function"]["arguments"]
                        
                        if tool_name and tool_args:
                            tool_call = {
                                "id": f"call_{uuid.uuid4().hex[:24]}",
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": json.dumps(tool_args) if isinstance(tool_args, dict) else tool_args
                                }
                            }
                            tool_calls.append(tool_call)
                            remaining_text = remaining_text.replace(match.group(0), "")
                            
                except json.JSONDecodeError:
                    try:
                        name_match = re.search(r'name\s*:\s*"([^"]+)"', match.group(0))
                        args_match = re.search(r'arguments\s*:\s*(\{[^}]+\})', match.group(0))
                        
                        if name_match and args_match:
                            tool_name = name_match.group(1)
                            tool_args = args_match.group(1)
                            
                            tool_call = {
                                "id": f"call_{uuid.uuid4().hex[:24]}",
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_args
                                }
                            }
                            tool_calls.append(tool_call)
                            remaining_text = remaining_text.replace(match.group(0), "")
                    except Exception:
                        continue
                except Exception:
                    continue
                    
        except Exception:
            continue
    
    return remaining_text.strip(), tool_calls


def parse_xml_tools(content: str) -> Tuple[str, List[Dict]]:
    """
    Parse XML tool calls từ content và trả về (text_content, tool_calls)
    """
    if not content or not isinstance(content, str):
        return content, []
    
    tool_pattern = r'<([a-zA-Z_][a-zA-Z0-9_]*)>\s*(.*?)\s*</\1>'
    
    tool_calls = []
    positions_to_remove = []
    
    matches = list(re.finditer(tool_pattern, content, re.DOTALL))
    
    for match in matches:
        tool_name = match.group(1)
        tool_content = match.group(2).strip()
        
        if not re.search(r'<\w+>', tool_content):
            continue
        
        param_pattern = r'<([a-zA-Z_][a-zA-Z0-9_]*)>(.*?)</\1>'
        params = {}
        param_matches = list(re.finditer(param_pattern, tool_content, re.DOTALL))
        
        for param_match in param_matches:
            param_name = param_match.group(1)
            param_value = param_match.group(2).strip()
            params[param_name] = param_value
        
        if not params:
            continue
        
        tool_call = {
            "id": f"call_{uuid.uuid4().hex[:24]}",
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(params)
            }
        }
        
        tool_calls.append(tool_call)
        positions_to_remove.append((match.start(), match.end()))
    
    remaining_text = content
    for start, end in reversed(positions_to_remove):
        remaining_text = remaining_text[:start] + remaining_text[end:]
    
    remaining_text = re.sub(r'\n\s*\n\s*\n', '\n\n', remaining_text.strip())
    
    return remaining_text, tool_calls

def enhance_response_with_tools(response: Dict) -> Dict:
    """
    Parse tool calls từ DeepSeek response và convert sang OpenAI format
    """
    if not response or "choices" not in response:
        return response
    
    for choice in response["choices"]:
        if "message" not in choice:
            continue
            
        message = choice["message"]
        content = message.get("content", "")
        
        if not content:
            continue
        
        remaining_text, tool_calls = parse_json_tools(content)
        
        if not tool_calls:
            remaining_text, tool_calls = parse_xml_tools(content)
        
        if tool_calls:
            tool_calls = validate_cline_compatible_tools(tool_calls)
        
        if tool_calls:
            message["content"] = remaining_text if remaining_text is not None else ""
            message["tool_calls"] = tool_calls
            choice["finish_reason"] = "tool_calls"
        else:
            if "content" not in message or message["content"] is None:
                message["content"] = content if content is not None else ""
            choice["finish_reason"] = "stop"
    
    return response

def validate_cline_compatible_tools(tool_calls: List[Dict]) -> List[Dict]:
    """
    Ensure tool calls are compatible with Cline's expected tool set
    Validates both tool names AND arguments structure
    """
    valid_tools = {
        'task_progress', 'read_file', 'write_to_file', 'replace_in_file', 
        'search_files', 'list_files', 'list_code_definition_names',
        'execute_command', 'ask_followup_question',
        'attempt_completion', 'use_mcp_tool', 'access_mcp_resource'
    }
    
    required_args = {
        'read_file': ['path'],
        'write_to_file': ['path', 'content'],
        'replace_in_file': ['path', 'diff'],
        'search_files': ['path', 'regex'],
        'list_files': ['path'],
        'list_code_definition_names': ['path'],
        'execute_command': ['command'],
        'task_progress': ['completed', 'remaining'],
        'attempt_completion': ['result'],
        'ask_followup_question': ['question']
    }
    
    validated_tools = []
    
    for tool in tool_calls:
        tool_name = tool.get('function', {}).get('name', '')
        
        if not tool_name:
            continue
        
        if tool_name not in valid_tools:
            continue
        
        arguments_str = tool.get('function', {}).get('arguments', '{}')
        
        try:
            arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
            
            if tool_name in required_args:
                missing_args = [arg for arg in required_args[tool_name] if arg not in arguments]
                
                if missing_args:
                    continue
            
            is_valid, error_msg = validate_tool_arguments(tool_name, arguments)
            
            if not is_valid:
                continue
            
            validated_tools.append(tool)
            
        except json.JSONDecodeError:
            continue
        except Exception:
            continue
    
    return validated_tools

def validate_tool_arguments(tool_name: str, arguments: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate tool arguments against expected schema
    Returns: (is_valid, error_message)
    """
    validators = {
        'read_file': lambda args: (
            'path' in args and isinstance(args['path'], str) and len(args['path']) > 0,
            "read_file requires 'path' as non-empty string"
        ),
        'write_to_file': lambda args: (
            'path' in args and 'content' in args and 
            isinstance(args['path'], str) and isinstance(args['content'], str),
            "write_to_file requires 'path' and 'content' as strings"
        ),
        'replace_in_file': lambda args: (
            'path' in args and 'diff' in args and
            isinstance(args['path'], str) and isinstance(args['diff'], str),
            "replace_in_file requires 'path' and 'diff' as strings"
        ),
        'search_files': lambda args: (
            'path' in args and 'regex' in args and
            isinstance(args['path'], str) and isinstance(args['regex'], str),
            "search_files requires 'path' and 'regex' as strings"
        ),
        'list_files': lambda args: (
            'path' in args and isinstance(args['path'], str),
            "list_files requires 'path' as string"
        ),
        'list_code_definition_names': lambda args: (
            'path' in args and isinstance(args['path'], str) and len(args['path']) > 0,
            "list_code_definition_names requires 'path' as non-empty string"
        ),
        'execute_command': lambda args: (
            'command' in args and isinstance(args['command'], str) and len(args['command']) > 0,
            "execute_command requires 'command' as non-empty string"
        ),
        'task_progress': lambda args: (
            'completed' in args and 'remaining' in args and
            isinstance(args['completed'], list) and isinstance(args['remaining'], list),
            "task_progress requires 'completed' and 'remaining' as arrays"
        ),
        'attempt_completion': lambda args: (
            'result' in args and isinstance(args['result'], str),
            "attempt_completion requires 'result' as string"
        ),
        'ask_followup_question': lambda args: (
            'question' in args and isinstance(args['question'], str) and len(args['question']) > 0,
            "ask_followup_question requires 'question' as non-empty string"
        )
    }
    
    if tool_name not in validators:
        return True, None
    
    validator = validators[tool_name]
    is_valid, error_msg = validator(arguments)
    
    return is_valid, error_msg if not is_valid else None