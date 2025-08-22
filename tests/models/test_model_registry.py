import pytest
from PAI.models.model_registry import ProviderRegistry


def test_model_registry_register_1():
    """
    Test registering a provider
    """
    ProviderRegistry._registry = {}

    @ProviderRegistry.register("test_provider")
    class TestProvider:
        def __init__(self, param):
            self.param = param

    assert "test_provider" in ProviderRegistry._registry
    assert ProviderRegistry._registry["test_provider"] == TestProvider


def test_model_registry_get_provider_1():
    """
    Test getting a provider
    """
    ProviderRegistry._registry = {}

    @ProviderRegistry.register("test_provider")
    class TestProvider:
        def __init__(self, param=None):
            self.param = param

    provider = ProviderRegistry.get_provider("test_provider")
    assert isinstance(provider, TestProvider)
    assert provider.param is None

    provider = ProviderRegistry.get_provider("test_provider", param="value")
    assert provider.param == "value"


def test_model_registry_get_registered_providers_1():
    """Test getting list of registered providers"""
    # Reset the registry for clean test
    ProviderRegistry._registry = {}

    @ProviderRegistry.register("provider1")
    class Provider1:
        def __init__(self, param):
            self.param = param

    @ProviderRegistry.register("provider2")
    class Provider2:
        def __init__(self, param):
            self.param = param

    providers = ProviderRegistry.get_registered_providers()
    assert set(providers) == {"provider1", "provider2"}
