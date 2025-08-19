import os
from typing import Optional, Dict, Any, List
from .models.session import ModelSession
from .models.model_registry import ProviderRegistry
# Import all providers to trigger registration
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
    
    def use_provider(self, provider: str, **kwargs) -> 'PAI':
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
    
    def use_openai(self, **kwargs) -> 'PAI':
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
            raise RuntimeError("No provider initialized. Call use_openai(), use_anthropic(), etc. first.")
        
        return self.session.generate(prompt, **kwargs)

    @classmethod
    def available_providers(cls) -> List[str]:
        """Get list of all registered providers"""
        return list(ProviderRegistry.get_registered_providers())

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
            raise RuntimeError("No provider initialized. Call use_provider() first.")
        
        return self.session.generate(prompt, **kwargs)
    
    def chat(self, prompt: str, **kwargs) -> str:
        """Alias for generate() - more intuitive for chat interactions"""
        return self.generate(prompt, **kwargs)
    
    def status(self) -> Dict[str, Any]:
        """Get current provider and model info"""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "initialized": self.session.provider is not None
        }
