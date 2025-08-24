import pytest
from PAI.models.Anthropic_client import AnthropicClient


def test_Anthropic_client_init_1():
    """Test initialization with API key provided as parameter"""
    client = AnthropicClient(api_key="test-key", model="claude-3-haiku-20240307")
    assert client.api_key == "test-key"
    assert client.model == "claude-3-haiku-20240307"


def test_Anthropic_client_init_2(monkeypatch):
    """Test initialization with API key from environment variable"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-test-key")
    client = AnthropicClient(model="claude-3-haiku-20240307")
    assert client.api_key == "env-test-key"
    assert client.model == "claude-3-haiku-20240307"


def test_Anthropic_client_generate_1(mocker):
    """Test generate method returns expected response"""

    class MockText:
        text = "Test response"

    class MockResponse:
        content = [MockText()]

    client = AnthropicClient(api_key="test-key")
    mocker.patch.object(client.client.messages, "create", return_value=MockResponse())

    result = client.generate("Test prompt")
    assert result == "Test response"


def test_Anthropic_client_generate_2():
    """Test error handling for empty prompts"""
    client = AnthropicClient(api_key="test-key")
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.generate("   ")
