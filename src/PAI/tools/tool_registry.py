import inspect
import json
import logging
from typing import Dict, Any, Callable, Optional, List

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for tools that can be used by AI models.

    Tools are registered using the @ToolRegistry.register() decorator.
    When modules containing decorated functions are imported,
    the functions are automatically added to the registry.
    """

    _tools = {}

    @classmethod
    def register(cls, name: str, description: str = None, params: Dict = None):
        """
        Decorator to register a function as a tool

        Args:
            name: Name of the tool
            description: Description of what the tool does
            params: Dictionary of parameters with their types and descriptions
                   Format: {
                      "param_name": {"type": "string|number|boolean|array|object", "description": "..."}
                   }
        """

        def decorator(func):
            # Use provided params or infer from function
            parameters = (
                cls._build_parameter_schema(params)
                if params
                else {"type": "object", "properties": {}}
            )

            cls._tools[name] = {
                "function": func,
                "description": description or func.__doc__ or "",
                "parameters": parameters,
            }
            logger.info(f"Registered tool: {name}")
            return func

        return decorator

    @classmethod
    def _build_parameter_schema(cls, params: Dict) -> Dict:
        """
        Build JSON Schema from params dictionary

        Args:
            params: Dictionary of parameter definitions

        Returns:
            JSON Schema for parameters
        """
        properties = {}
        required = []

        for param_name, param_info in params.items():
            param_type = param_info.get("type", "string")

            # Convert "numeric" type to "number" for JSON Schema compatibility
            if param_type == "numeric":
                param_type = "number"

            prop = {"type": param_type}

            # Add description if present
            if "description" in param_info:
                prop["description"] = param_info["description"]

            # Add enum if present
            if "enum" in param_info:
                prop["enum"] = param_info["enum"]

            # Add other JSON Schema validations if present
            for key in [
                "minimum",
                "maximum",
                "minLength",
                "maxLength",
                "pattern",
                "format",
            ]:
                if key in param_info:
                    prop[key] = param_info[key]

            properties[param_name] = prop

            # Parameter is required unless it has a default value
            if "default" not in param_info:
                required.append(param_name)

        return {"type": "object", "properties": properties, "required": required}

    @classmethod
    def get_tools(cls) -> List[Dict]:
        """
        Get all registered tool definitions in a generic format

        Returns:
            List of tool definitions with name, description and parameters
        """
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"],
            }
            for name, info in cls._tools.items()
        ]

    @classmethod
    def execute_tool(cls, name: str, args: Dict[str, Any]) -> Any:
        """Execute a registered tool"""
        if name not in cls._tools:
            logger.error(f"Tool not found: {name}")
            return {"error": f"Unknown tool: {name}"}

        try:
            result = {}

            func = cls._tools[name]["function"]
            logger.info(f"Executing tool: {name} with args: {args}")
            func_result = func(**args)
            result = {
                "func_name": name,
                "func_args": args,
                "func_results": func_result,
            }
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"error": str(e)}

    @classmethod
    def has_tools(cls) -> bool:
        """Check if any tools are registered"""
        return len(cls._tools) > 0
