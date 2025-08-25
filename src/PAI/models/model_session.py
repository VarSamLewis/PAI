from .model_registry import ProviderRegistry

from PAI.utils.logger import logger


class ModelSession:
    def __init__(self):
        self.provider = None

    def init(self, provider_name: str, **kwargs):
        """Initialize session with a provider"""
        logger.info(f"Initializing session with provider: {provider_name}")
        self.provider = ProviderRegistry.get_provider(provider_name, **kwargs)

    def generate(self, prompt: str, **kwargs):
        if not self.provider:
            raise RuntimeError("Session not initialized. Call init() first.")
        return self.provider.generate(prompt, **kwargs)
