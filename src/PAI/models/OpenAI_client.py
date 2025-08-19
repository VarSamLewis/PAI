import os
from openai import OpenAI
from .model_registry import ProviderRegistry
from . import systemprompt

@ProviderRegistry.register("openai")
class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7):
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": systemprompt.system_prompt},
                {"role": "user", "content": prompt}
                ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()
