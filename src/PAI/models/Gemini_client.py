import os
from google import genai
from .model_registry import ProviderRegistry
from . import systemprompt

from PAI.utils.logger import logger


@ProviderRegistry.register("gemini")
class GeminiClient:
    def __init__(
        self, api_key: str = None, model: str = None, **kwargs
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or "gemini-2.0-flash-exp"
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs):
        if not prompt.strip():
            logger.error("Prompt cannot be empty")
            raise ValueError("Prompt cannot be empty")

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            **{k: v for k, v in kwargs.items() if k not in {"model"}}
        )


        return resp.text
