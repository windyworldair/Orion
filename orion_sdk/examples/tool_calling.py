"""
Orion SDK — Tool Calling Example
===================================
Send tool definitions to the model and handle structured tool calls.
"""

from orion_sdk import create_client, ToolDefinition, Message

client = create_client("openai", api_key="sk-YOUR_OPENAI_KEY")

# ── Define your tools ─────────────────────────────────────────────
tools = [
    ToolDefinition(
        name="get_weather",
        description="Get the current weather for a city",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Tokyo'",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit",
                },
            },
            "required": ["city"],
        },
    ),
    ToolDefinition(
        name="calculate",
        description="Evaluate a mathematical expression",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression, e.g. '2 + 3 * 4'",
                },
            },
            "required": ["expression"],
        },
    ),
]

# ── First request — model decides to call a tool ──────────────────
response = client.complete(
    "What's the weather in Paris and what is 25 * 17?",
    tools=tools,
    model="gpt-4o",
    temperature=0,
)

print("=== Model Requested Tool Calls ===")
if response.has_tool_calls:
    messages = [Message.user("What's the weather in Paris and what is 25 * 17?")]

    # Handle each tool call
    for tool_call in response.tool_calls:
        print(f"  Tool: {tool_call.name}")
        print(f"  Args: {tool_call.arguments}")
        print()

        # Simulate executing the tools
        if tool_call.name == "get_weather":
            city = tool_call.arguments.get("city", "Unknown")
            result = {"temperature": 18, "condition": "Partly cloudy", "city": city}
        elif tool_call.name == "calculate":
            expr = tool_call.arguments.get("expression", "0")
            try:
                result = {"expression": expr, "result": eval(expr)}  # noqa: S307
            except Exception as e:
                result = {"expression": expr, "error": str(e)}
        else:
            result = {"error": f"Unknown tool: {tool_call.name}"}

        # Add the tool call and result to the conversation
        messages.append(Message.tool(str(result), tool_call_id=tool_call.id))

    # ── Second request — model processes tool results ─────────────
    print("=== Sending Tool Results Back ===")
    response = client.complete(
        messages=messages,
        tools=tools,
        model="gpt-4o",
        temperature=0,
    )

    print(f"\nFinal answer:\n{response.content}")
    print(f"Provider: {response.provider}")
    print(f"Model: {response.model}")
else:
    print("No tool calls — model answered directly:")
    print(response.content)

# ── Simple single-tool example ────────────────────────────────────
print("\n\n=== Simple Tool Call Example ===")

response = client.complete(
    "What's 997 * 1,023?",
    tools=[tools[1]],  # Only the calculate tool
    model="gpt-4o",
)

if response.has_tool_calls:
    for tc in response.tool_calls:
        print(f"Called: {tc.name}({tc.arguments})")
