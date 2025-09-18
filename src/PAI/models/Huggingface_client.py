import os
from huggingface_hub import InferenceClient
import anthropic
from .model_registry import ProviderRegistry
from . import systemprompt

from PAI.utils.logger import logger


@ProviderRegistry.register("huggingface")
class HuggingfaceClient:
    def __init__(
        self,
        api_key: str = None,
        model: str = "meta-llama/Llama-3.1-8B-Instruct",
        **kwargs
    ):
        self.api_key = api_key or os.getenv("HUGGINGFACE_INFERENCE_TOKEN")
        self.model = model
        self.client = InferenceClient(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs):
        if not prompt.strip():
            logger.error("Prompt cannot be empty")
            raise ValueError("Prompt cannot be empty")

        if not self.api_key:
            logger.error(
                "No Hugging Face API key found. Set HUGGINGFACE_INFERENCE_TOKEN environment variable or pass api_key parameter."
            )
            raise ValueError("Hugging Face API key is required")

        system_prompt = kwargs.get("system", systemprompt.system_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        gen_kwargs = {k: v for k, v in kwargs.items() if k not in {"model", "system"}}

        resp = self.client.chat_completion(
            messages=messages, model=self.model, **gen_kwargs
        )

        return resp.choices[0].message.content
