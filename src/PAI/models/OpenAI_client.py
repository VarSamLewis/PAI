import os
from openai import OpenAI
from .model_registry import ProviderRegistry
from . import systemprompt


@ProviderRegistry.register("openai")
class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", **kwargs):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs):
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        params = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": systemprompt.system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        # Prevent overriding reserved parameters
        reserved = {"model", "messages"}
        for k, v in kwargs.items():
            if k not in reserved:
                params[k] = v

        resp = self.client.chat.completions.create(**params)
        return resp.choices[0].message.content.strip()
