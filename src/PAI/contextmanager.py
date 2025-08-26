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
        resource_metadata = ResourceRegistry.get_resource_metadata()
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
            Capabilities banner (tools/resources available this session):

        TOOLS:
        {json.dumps(tool_list, indent=2)}

        RESOURCES:
        {json.dumps(resource_metadata, indent=2)}
        """.strip()

        self.meta_prompt = meta_prompt_text
        logger.info("Meta prompt context created.")
        return meta_prompt_text

    def build_next_prompt(
        self,
        original_prompt: str,
        tool_results: List[Dict[str, Any]],
        resource_results: List[Dict[str, Any]],
    ) -> str:
        """
        Build the next prompt using tool and resource results.
        The system prompt should already encode the protocol:
        - If more tools/resources are needed, emit ONLY the JSON request.
        - Otherwise, answer based strictly on results.
        """
        logger.debug("Building next prompt from tool/resource results.")

        tool_results_json = json.dumps(tool_results, indent=2)

        resource_contents: List[str] = []
        for res in resource_results:
            content = res.get("Content")
            if content:
                resource_contents.append(content)

        resource_contents_text = (
            "\n".join(resource_contents)
            if resource_contents
            else "No resource content found."
        )

        next_prompt = f"""
        You are given tool execution results and resource contents. Use these to proceed to formulate .

        Tool results:
        {tool_results_json}

        Resource contents:
        {resource_contents_text}

        If you still need more tools or resources, provide JSON blocks per the protocol and no prose. 
        Otherwise, provide the best final answer based strictly on the above. 
        Original question: {original_prompt}
        """.strip()

        logger.info("Next prompt constructed for iterative step.")
        return next_prompt
