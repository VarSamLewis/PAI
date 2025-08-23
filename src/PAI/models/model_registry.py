class ProviderRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a provider class by name"""

        def inner_wrapper(wrapped_class):
            cls._registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_provider(cls, name: str, **kwargs):
        if name not in cls._registry:
            raise ValueError(f"Unknown provider: {name}")
        return cls._registry[name](**kwargs)

    @classmethod
    def get_registered_providers(cls):
        """Returns a list of all registered provider names"""
        return cls._registry.keys()
