"""
Example custom plugin for Advanced Claude Proxy.
"""

TOOL_SCHEMA = {
    "name": "get_local_weather",
    "description": "Returns the current weather for a local city. This is executed securely on the proxy host.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city to get the weather for."
            }
        },
        "required": ["city"]
    }
}

def execute(city: str) -> str:
    """The function that gets executed when Claude calls this tool."""
    # In reality, this could query a local DB or an internal API
    return f"The weather in {city} is currently 22°C and sunny. (Mocked by local plugin)"
