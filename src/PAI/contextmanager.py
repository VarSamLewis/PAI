import json
import logging
from typing import Dict, Any, Optional, List
from .tools.tool_registry import ToolRegistry
from .resources.resource_registry import ResourceRegistry

logger = logging.getLogger(__name__)


class ContentManager:
    def __init__(self) -> None:
        self.tools_available: Optional[List[Dict[str, Any]]] = None
        self.resources_available: Optional[List[Dict[str, Any]]] = None
        self.meta_prompt: Optional[str] = None

    def get_tool_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the list of available tools.
        """
        logger.debug("Attempting to get tool list.")
        if not ToolRegistry.has_tools():
            logger.warning("No tools available in ToolRegistry.")
            return None
        tool_list = ToolRegistry.get_tools()
        self.tools_available = tool_list
        logger.info(f"Tool list retrieved: {tool_list}")
        return tool_list

    def get_resource_metadata(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the metadata for available resources.
        """
        logger.debug("Attempting to get resource metadata.")
        resource_metadata = ResourceRegistry.get_tool_metadata()
        self.resources_available = resource_metadata
        logger.info(f"Resource metadata retrieved: {resource_metadata}")
        return resource_metadata

    def create_prompt_context(self) -> str:
        """
        Create a meta prompt context string including available tools and resources.
        """
        logger.debug("Creating prompt context.")
        tool_list = self.get_tool_list()
        resource_metadata = self.get_resource_metadata()
        meta_prompt_text = f"""
            You can call tools from this list {json.dumps(tool_list, indent=2)} using this format:
                            ```
            {{
                "name": "tool_name",
                "args": {{
                    "param1": "value1",
                    "param2": "value2"
                }}
                }}
            ```             You can also call for resources from this list {json.dumps(resource_metadata, indent=2)} using this format:         ``` 
         {{
              "Name": "example_resource",
              "ID": "89d32618-3532-449a-9d67-9b455ff12054",
              "Description": "An example resource for demonstration purposes",
              "ContentType": "file"
             }}
         ```        """
        self.meta_prompt = meta_prompt_text
        logger.info("Meta prompt context created.")
        return meta_prompt_text
