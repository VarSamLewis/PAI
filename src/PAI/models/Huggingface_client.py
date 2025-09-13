
import os
from huggingface_hub import InferenceClient
import anthropic
from .model_registry import ProviderRegistry
from . import systemprompt

from PAI.utils.logger import logger

@ProviderRegistry.register("huggingface")
class HuggingfaceClient:
    def __init__(
        self, api_key: str = None, model: str = "meta-llama/Llama-3.1-8B-Instruct", **kwargs
    ):
        self.api_key = api_key or os.getenv("HUGGINGFACE_INFERENCE_TOKEN")
        self.model = model
        self.client =  InferenceClient(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs):
        if not prompt.strip():
            logger.error("Prompt cannot be empty")
            raise ValueError("Prompt cannot be empty")

        system_prompt = kwargs.get("system", systemprompt.system_prompt)
        full_prompt = system_prompt + prompt

        gen_kwargs = {k: v for k, v in kwargs.items() if k not in {"model", "system"}}

        resp = self.client.text_generation(
            prompt=full_prompt,
            model=self.model,
            **gen_kwargs
        )
        return resp
