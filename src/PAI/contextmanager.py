import json
import logging
from typing import Dict, Any, Optional, List
from .tools.tool_registry import ToolRegistry
from .resources.resource_registry import ResourceRegistry

from PAI.utils.logger import logger


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

    def create_prompt_context(self, session_log: dict) -> str:
        """
        Create a meta prompt context string including available tools and resources.
        """
        logger.debug("Creating prompt context.")

        if session_log:
            tool_list = session_log.get("tool_metadata", [])
            resource_metadata = session_log.get("resource_metadata", [])
        else:
            tool_list = self.get_tool_list()
            resource_metadata = self.get_resource_metadata()

        meta_prompt_text = f"""
            You have access to the following tools and resources.

            TOOLS:
            {json.dumps(tool_list, indent=2)}

            RESOURCES:
            {json.dumps(resource_metadata, indent=2)}

            When answering, if you need to use a tool or resource, you MUST include a JSON block in your response using the format below.
            After the JSON block, provide a plaintext answer using the content of the resource or tool result.

            Tool call format:
            Tool Request(s):
            {{
              "name": "tool_name",
              "args": {{
                "param1": "value1",
                "param2": "value2"
              }}
            }}

            Resource call format:
            Request Request(s):
            {{
              "Name": "resource_name",
              "ID": "resource_id",
              "Description": "resource description",
              "ContentType": "file or string"
            }} """

        self.meta_prompt = meta_prompt_text
        logger.info("Meta prompt context created.")
        return meta_prompt_text
