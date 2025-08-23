import os
import json
import re
from typing import Optional, Dict, Any, List
from .models.session import ModelSession
from .models.model_registry import ProviderRegistry
from .tools.tool_registry import ToolRegistry
from .resources.resource_registry import ResourceRegistry
from .contextmanager import ContentManager
from .models.OpenAI_client import OpenAIClient

# Add more imports as you create providers:
# from .models.anthropic_client import AnthropicClient
# from .models.huggingface_client import HuggingFaceClient
# from .models.local_client import LocalClient


class PAI:
    """
    Unified interface for all AI model providers
    """

    def __init__(self):
        self.session = ModelSession()
        self.current_provider = None
        self.current_model = None
        self.tool_enabled = True

    def use_provider(self, provider: str, **kwargs) -> "PAI":
        """
        Initialize any provider with the given arguments

        Args:
            provider: Name of the provider to use (openai, anthropic, etc.)
            **kwargs: Provider-specific parameters

        Returns:
            Self for method chaining
        """
        self.session.init(provider, **kwargs)
        self.current_provider = provider
        self.current_model = kwargs.get("model")
        return self

    def use_openai(self, **kwargs) -> "PAI":
        """Initialize OpenAI provider - passes all arguments directly to OpenAIClient"""
        return self.use_provider("openai", **kwargs)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using the current provider

        Args:
            prompt: The input prompt
            **kwargs: Provider-specific parameters (max_tokens, temperature, etc.)

        Returns:
            Generated response string
        """
        if not self.session.provider:
            raise RuntimeError(
                "No provider initialized. Call use_openai(), use_anthropic(), etc. first."
            )
        if self.tool_enabled:
            context = ContentManager()

            prompt = prompt + context.create_prompt_context()
        return self.session.generate(prompt, **kwargs)

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
            Final response, either original or with tool results
        """
        if not self.tool_enabled:
            return response

        tool_calls = self._extract_tool_calls(response)

        if not tool_calls:
            return response

        tool_results = self.call_tools(tool_calls)

        results_text = json.dumps(tool_results, indent=2)

        tool_prompt = f"""
        Based on the original request: {original_prompt}

        You responded with: {response}

        I executed the tool(s) you requested, and here are the results:
        {results_text}

        Please provide your final answer incorporating these tool results.
        """

        final_response = self.session.generate(tool_prompt, **kwargs)
        return final_response

    def _extract_tool_calls(self, text: str) -> List[Dict]:
        """
        Extract tool calls from text

        Args:
            text: Text to search for tool calls

        Returns:
            List of tool call dictionaries or empty list if none found
        """
        tool_calls = []

        pattern = r"```(?:json)?\s*({[\s\S]*?})\s*```"
        matches = re.findall(pattern, text)

        for match in matches:
            try:
                data = json.loads(match)
                if "name" in data and "args" in data:
                    tool_calls.append(data)
            except json.JSONDecodeError:
                continue

        if not tool_calls:
            # More lenient pattern for standalone JSON
            pattern = r'{[\s\S]*?"name"[\s\S]*?"args"[\s\S]*?}'
            matches = re.findall(pattern, text)

            for match in matches:
                try:
                    data = json.loads(match)
                    if "name" in data and "args" in data:
                        tool_calls.append(data)
                except json.JSONDecodeError:
                    continue

        return tool_calls

    @classmethod
    def available_providers(cls) -> List[str]:
        """Get list of all registered providers"""
        return list(ProviderRegistry.get_registered_providers())

    def chat(self, prompt: str, **kwargs) -> str:
        """Alias for generate() - more intuitive for chat interactions"""
        return self.generate(prompt, **kwargs)

    def status(self) -> Dict[str, Any]:
        """Get current provider and model info"""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "initialized": self.session.provider is not None,
        }
