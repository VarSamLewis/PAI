import os
import anthropic
from .model_registry import ProviderRegistry
from . import systemprompt

from PAI.utils.logger import logger


@ProviderRegistry.register("anthropic")
class AnthropicClient:
    def __init__(
        self, api_key: str = None, model: str = None, **kwargs
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or "claude-3-haiku-20240307"
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs):
        if not prompt.strip():
            logger.error("Prompt cannot be empty")
            raise ValueError("Prompt cannot be empty")

        max_tokens = kwargs.get("max_tokens", 300)
        system_prompt = kwargs.get("system", systemprompt.system_prompt)

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Prevent overriding reserved parameters
        reserved = {"model", "max_tokens", "system", "messages"}
        for k, v in kwargs.items():
            if k not in reserved:
                params[k] = v
                logger.debug(f"Setting custom parameter: {k}={v}")

        resp = self.client.messages.create(**params)
        return resp.content[0].text
