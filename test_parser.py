from core.tool_parser import parse_xml_tools

# Test case
test_content = """I need to examine the current files to understand the task and create a plan. Let me start by reading the visible files to see what we're working with.

<read_file>
<path>src/background/deepseek/prompt-template.ts</path>
</read_file>"""

remaining, tools = parse_xml_tools(test_content)

import json
