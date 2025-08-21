from .tool_registry import ToolRegistry

# Example of how to add tools to the registry.
@ToolRegistry.register(
    name="sum2num",
    description="Adds 2 numbers",
    params={
        "a": {"type": "number", "description": "First number"},
        "b": {"type": "number", "description": "Second number"}
    }
)
def sum2num(a, b):
    """Adds two numbers together"""
    return a + b