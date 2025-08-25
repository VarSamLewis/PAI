import os
import json
import re
from datetime import datetime 
from pathlib import Path
from typing import Optional, Dict, Any, List
from .models.model_session import ModelSession
from .models.model_registry import ProviderRegistry
from .tools.tool_registry import ToolRegistry
from .resources.resource_registry import ResourceRegistry
from .contextmanager import ContentManager
from .models.OpenAI_client import OpenAIClient
from .models.Anthropic_client import AnthropicClient

# Add more imports as you create providers:
# from .models.huggingface_client import HuggingFaceClient
# from .models.local_client import LocalClient

from PAI.utils.logger import logger


class PAI:
    """
    Unified interface for all AI model providers
    """
    def __init__(self, session_name):
        self.model_session = ModelSession()
        self.current_provider = None
        self.current_model = None
        self.tool_enabled = True  # Q does implementation this mean I can't set this to false?
        self.resource_enabled = True
        self.session_file = Path.home() / f".PAI/PAI_session_logs/PAI_session_log_{session_name}.json"
        self.context = ContentManager()

    def init_session(self, session_name, provider, model, api_key=None):
        try:
            from .tools import tool_store
            from .resources import resource_store
            logger.debug("Stores ran")
        except ImportError:
            logger.warning("Failed to import stores")
            pass
        tool_list = ToolRegistry.get_tools()
        resource_metadata = ResourceRegistry.get_tool_metadata()

        self.session_log = {
            "session_name": session_name,
            "session_start_dt": datetime.utcnow().isoformat() + "Z",
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "tool_metadata": tool_list,
            "resource_metadata": resource_metadata,
            "prompt_history": []
        }
        self.use_provider(provider, model=model, api_key=api_key)

    def save_session(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(self.session_log, f, indent=2)
            logger.info(f"Session data saved: {self.session_file}")

    def load_session(self):
        """Load existing session from file"""
        with open(self.session_file, "r") as f:
            self.session_log = json.load(f)
        self.use_provider(
            self.session_log["provider"],
            model=self.session_log["model"],
            api_key=self.session_log.get("api_key")
        )

    @classmethod
    def get_session_log(self):
        """Load existing session log from file"""
        with open(self.session_file, "r") as f:
            current_session_file = json.load(f)
            logger.debug(f"Session data loaded: {self.session_file}")
        return current_session_file

    @classmethod
    def create_ai_from_session_log(cls, session_file: Optional[Path] = None) -> "PAI":
        """Create PAI instance from saved session_loguration"""
        if session_file is None:
            session_file = cls.session_file

        session_log = cls.get_session_log()

        ai = cls()
        provider = session_log["provider"]
        model = session_log["model"]
        api_key = session_log.get("api_key")

        kwargs = {"model": model}
        if api_key:
            kwargs["api_key"] = api_key

        ai.use_provider(provider, **kwargs)

        return ai

    def add_prompt(self, prompt, response):
        if "prompt_history" not in self.session_log:
            self.session_log["prompt_history"] = []
        self.session_log["prompt_history"].append({"prompt": prompt, "response": response})
        self.save_session()
        logger.info("Prompt and response added to session log")

    def use_provider(self, provider: str, **kwargs) -> "PAI":
        """
        Initialize any provider with the given arguments

        Args:
            provider: Name of the provider to use (openai, anthropic, etc.)
            **kwargs: Provider-specific parameters

        Returns:
            Self for method chaining
        """
        self.model_session.init(provider, **kwargs)
        self.current_provider = provider
        self.current_model = kwargs.get("model")
        logger.info(f"Using provider: {provider} with model: {self.current_model}")
        return self

    def use_openai(self, **kwargs) -> "PAI":
        """Initialize OpenAI provider - passes all arguments directly to OpenAIClient"""
        return self.use_provider("openai", **kwargs)

    def use_anthropic(self, **kwargs) -> "PAI":
        """Initialize Anthropic provider - passes all arguments directly to AnthropicClient"""
        return self.use_provider("anthropic", **kwargs)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using the current provider

        Args:
            prompt: The input prompt
            **kwargs: Provider-specific parameters (max_tokens, temperature, etc.)

        Returns:
            Generated response string
        """
        if not self.model_session.provider:
            logger.error("No provider initialized. Call use_openai(), use_anthropic(), etc. first.")
            raise RuntimeError("No provider initialized. Call use_openai(), use_anthropic(), etc. first.")
            
        if self.tool_enabled:
            prompt = prompt + self.context.create_prompt_context(self.session_log)
            logger.debug(f"Prompt with context: {prompt}")
        return self.model_session.generate(prompt, **kwargs)

    def call_tools(self, tool_list: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for request in tool_list:
            if "name" not in request or "args" not in request:
                results.append({"error": "Invalid tool request format"})
                continue

            tool_name = request["name"]
            tool_args = request["args"]
            result = ToolRegistry.execute_tool(tool_name, tool_args)
            results.append(result)
            logger.debug(f"Tool result: {results}")

        return results

    def call_resources(self, resource_list: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        seen = set()
        for request in resource_list:
            name = request.get("Name") or request.get("name")
            resource_id = request.get("ID")
            key = (name, resource_id)
            if key in seen:
                continue
            seen.add(key)
            if not name:
                results.append({"error": "Invalid resource request format"})
                continue
            result = ResourceRegistry.get_resource(name, resource_id)
            results.append(result)
            logger.debug(f"Resource result: {results}")

        return results

    def evaluate_response(self, original_prompt: str, response: str, **kwargs) -> str:
        """
        Evaluate if the response contains tool usage, execute tools if needed,
        and regenerate response with tool results

        Args:
            original_prompt: The original user prompt
            response: The initial LLM response
            **kwargs: Generation parameters

        Returns:
            Final response, either original or with tool results/resource requests
        """

        if not self.tool_enabled and not self.resource_enabled:
            return response

        tool_calls = self._extract_tool_calls(response)
        request_calls = self._extract_resouce_call(response)

        if not tool_calls and request_calls:
            return response

        tool_results = self.call_tools(tool_calls)


        tool_results_json = json.dumps(tool_results, indent=2)

        resource_results = self.call_resources(request_calls)
        resource_results_json = json.dumps(resource_results, indent=2)

        resource_contents = []
        for res in resource_results:
            content = res.get("Content")
            if content:
                resource_contents.append(content)
        resource_contents_text = "\n".join(resource_contents) if resource_contents else "No resource content found."

        new_prompt = f"""
         Here is the results from the tools you requested:
         {tool_results_json}
         Here is the actual content of the resource you requested:
         {resource_contents_text}
         IMPORTANT: Only use the information in the resource content above to answer the question. Do NOT guess or use outside knowledge. If the answer is not present, say "I can't find the answer in the resource."
         Please answer: {original_prompt}
        """
        tools_parameters_used = [tool_call for tool_call in tool_calls]
        resource_parameters_used = [request_call for request_call in request_calls]

        final_response = self.model_session.generate(new_prompt, **kwargs)
        return final_response, tools_parameters_used, resource_parameters_used

    def _extract_tool_calls(self, text: str) -> List[Dict]:
        """
        Extract tool calls from text

        Args:
            text: Text to search for tool calls

        Returns:
            List of tool call dictionaries or empty list if none found
        """
        tool_calls = []

        tool_label = "Tool Request(s):"
        chunks = text.split(tool_label)[1:]
        for chunk in chunks:
            match = re.search(r'\{[\s\S]*?"name"[\s\S]*?"args"[\s\S]*?\}', chunk)
            if match:
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                    if "name" in data and "args" in data:
                        tool_calls.append(data)
                except json.JSONDecodeError:
                    continue

        # Also match standalone JSON objects (for compatibility)
        standalone_pattern = r'\{[\s\S]*?"name"[\s\S]*?"args"[\s\S]*?\}'
        standalone_matches = re.findall(standalone_pattern, text)
        for match in standalone_matches:
            try:
                data = json.loads(match)
                if "name" in data and "args" in data and data not in tool_calls:
                    tool_calls.append(data)
            except json.JSONDecodeError:
                continue

        logger.debug(f"Tools extracted: {tool_calls}")
        return tool_calls

    def _extract_resouce_call(self, text: str):
        resource_calls = []

        resource_label = "Request Resource(s):"  
        chunks = text.split(resource_label)[1:]
        for chunk in chunks:
            match = re.search(r'\{[\s\S]*?"Name"[\s\S]*?\}', chunk)
            if match:
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                    if "Name" in data:
                        resource_calls.append(data)
                except json.JSONDecodeError:
                    continue

        standalone_pattern = r'\{[\s\S]*?"Name"[\s\S]*?\}'
        standalone_matches = re.findall(standalone_pattern, text)
        for match in standalone_matches:
            try:
                data = json.loads(match)
                if "Name" in data and data not in resource_calls:
                    resource_calls.append(data)
            except json.JSONDecodeError:
                continue
        
        logger.debug(f"Resources extracted: {resource_calls}")
        return resource_calls

    def reset(self,):
        """Close the current PAI session and clear session data"""
        logger.info("Reset current session")
        self.session_log = None
        self.session_active = False
        self.current_provider = None
        self.current_model = None

    @classmethod
    def available_providers(cls) -> List[str]:
        """Get list of all registered providers"""
        return list(ProviderRegistry.get_registered_providers())

    def chat(self, prompt: str, **kwargs) -> str:
        """Alias for generate() - more intuitive for chat interactions"""
        return self.generate(prompt, **kwargs)

    def status(self) -> Dict[str, Any]:
        """Get current provider and model info"""
        logger.debug("Fetching session status")
        return {
            "session_name": self.session_log.get("session_name") if self.session_log else None,
            "session_start_dt": self.session_log.get("session_start_dt") if self.session_log else None,
            "provider": self.current_provider,
            "model": self.current_model,
            "initialized": self.model_session.provider is not None,
        }