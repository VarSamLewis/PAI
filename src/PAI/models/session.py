from .model_registry import ProviderRegistry


class ModelSession:
    def __init__(self):
        self.provider = None

    def init(self, provider_name: str, **kwargs):
        """Initialize session with a provider"""
        self.provider = ProviderRegistry.get_provider(provider_name, **kwargs)

    def generate(self, prompt: str, **kwargs):
        if not self.provider:
            raise RuntimeError("Session not initialized. Call init() first.")
        return self.provider.generate(prompt, **kwargs)
