import pytest
from PAI.models.model_session import ModelSession
from PAI.models.model_registry import ProviderRegistry


def test_session_init_1():
    """Test initializing a session with a provider"""
    ProviderRegistry._registry = {}

    @ProviderRegistry.register("test_provider")
    class TestProvider:
        def __init__(self, model="default"):
            self.model = model
            self.called = False

        def generate(self, prompt, **kwargs):
            self.called = True
            self.last_prompt = prompt
            self.last_kwargs = kwargs
            return f"Response to: {prompt}"

    session = ModelSession()
    session.init("test_provider", model="test_model")

    assert session.provider is not None
    assert isinstance(session.provider, TestProvider)
    assert session.provider.model == "test_model"


def test_session_generate_1():
    """Test generating responses through the session"""
    ProviderRegistry._registry = {}

    @ProviderRegistry.register("test_provider")
    class TestProvider:
        def __init__(self):
            self.called = False

        def generate(self, prompt, **kwargs):
            self.called = True
            self.last_prompt = prompt
            self.last_kwargs = kwargs
            return f"Response to: {prompt}"

    session = ModelSession()
    session.init("test_provider")

    response = session.generate("Test prompt", temperature=0.7)

    assert session.provider.called
    assert session.provider.last_prompt == "Test prompt"
    assert session.provider.last_kwargs == {"temperature": 0.7}
    assert response == "Response to: Test prompt"


def test_session_generate_2():
    """Test error handling when generating without initialization"""
    session = ModelSession()

    with pytest.raises(RuntimeError, match="Session not initialized"):
        session.generate("This should fail")
