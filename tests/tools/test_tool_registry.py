import pytest
from PAI.tools.tool_registry import ToolRegistry


def test_tool_registry_register_1():

    ToolRegistry._tools = {}

    params = {
        "arg1": {"type": "string", "description": "First argument"},
        "arg2": {
            "type": "string",
            "description": "Second argument",
            "default": "default",
        },
    }

    @ToolRegistry.register("test_tool", "Test description", params=params)
    def func(arg1, arg2="default"):
        return arg1 + arg2

    assert "test_tool" in ToolRegistry._tools
    assert ToolRegistry._tools["test_tool"]["function"] == func
    assert ToolRegistry._tools["test_tool"]["description"] == "Test description"

    assert (
        ToolRegistry._tools["test_tool"]["parameters"]["properties"]["arg1"]["type"]
        == "string"
    )
    assert (
        ToolRegistry._tools["test_tool"]["parameters"]["properties"]["arg2"][
            "description"
        ]
        == "Second argument"
    )

    assert "arg1" in ToolRegistry._tools["test_tool"]["parameters"]["required"]
    assert "arg2" not in ToolRegistry._tools["test_tool"]["parameters"]["required"]


def test_tool_registry_build_parameter_schema_1():
    """Test parameter schema building"""

    ToolRegistry._tools = {}

    params = {
        "required_param": {"type": "string", "description": "Required parameter"},
        "optional_param": {"type": "number", "default": 10, "minimum": 0},
        "enum_param": {"type": "string", "enum": ["option1", "option2"]},
        "numeric_param": {"type": "numeric", "maximum": 100},
    }

    schema = ToolRegistry._build_parameter_schema(params)

    assert schema["type"] == "object"
    assert "required_param" in schema["properties"]
    assert schema["properties"]["required_param"]["type"] == "string"
    assert schema["properties"]["required_param"]["description"] == "Required parameter"

    assert "numeric_param" in schema["properties"]
    assert schema["properties"]["numeric_param"]["type"] == "number"

    assert "required_param" in schema["required"]
    assert "optional_param" not in schema["required"]

    assert schema["properties"]["enum_param"]["enum"] == ["option1", "option2"]
    assert schema["properties"]["optional_param"]["minimum"] == 0
    assert schema["properties"]["numeric_param"]["maximum"] == 100


def test_tool_registry_get_tools_1():
    """Test retrieving registered tools"""

    ToolRegistry._tools = {}

    @ToolRegistry.register("tool1", "Tool 1 description")
    def tool1_func():
        pass

    @ToolRegistry.register("tool2", "Tool 2 description")
    def tool2_func():
        pass

    tools = ToolRegistry.get_tools()

    assert len(tools) == 2
    assert {
        "name": "tool1",
        "description": "Tool 1 description",
        "parameters": {"type": "object", "properties": {}},
    } in tools
    assert {
        "name": "tool2",
        "description": "Tool 2 description",
        "parameters": {"type": "object", "properties": {}},
    } in tools


def test_tool_registry_execute_tool():
    """Test executing a registered tool"""

    ToolRegistry._tools = {}

    @ToolRegistry.register("adder")
    def add(x, y):
        return x + y

    result = ToolRegistry.execute_tool("adder", {"x": 5, "y": 3})

    assert result["func_name"] == "adder"
    assert result["func_args"] == {"x": 5, "y": 3}
    assert result["func_results"] == 8


def test_tool_registry__execute_tool_2():
    """Test error handling when tool not found"""

    ToolRegistry._tools = {}

    result = ToolRegistry.execute_tool("nonexistent_tool", {})
    assert "error" in result
    assert "Unknown tool" in result["error"]


def test_tool_registry_execute_tool_3():
    """Test error handling during tool execution"""

    ToolRegistry._tools = {}

    @ToolRegistry.register("problematic")
    def problem_tool():
        raise ValueError("Something went wrong")

    result = ToolRegistry.execute_tool("problematic", {})
    assert "error" in result
    assert "Something went wrong" in result["error"]


def test_tool_registry_has_tools_1():
    """Test has_tools check"""

    ToolRegistry._tools = {}

    assert not ToolRegistry.has_tools()

    @ToolRegistry.register("some_tool")
    def some_func():
        pass

    assert ToolRegistry.has_tools()
