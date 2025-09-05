from .tool_registry import ToolRegistry


# Example of how to add tools to the registry.
@ToolRegistry.register(
    name="sum2num",
    description="Adds 2 numbers",
    params={
        "a": {"type": "number", "description": "First number"},
        "b": {"type": "number", "description": "Second number"},
    },
)
def sum2num(a, b):
    """Adds two numbers together"""
    return a + b


@ToolRegistry.register(
    name="getlocalfile",
    description="Reads a local file and returns its content",
    params={
        "file_path": {"type": "string", "description": "Path to the local file"},
    },
)
def getlocalfile(file_path: str) -> str:
    """Reads a local file and returns its content"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
