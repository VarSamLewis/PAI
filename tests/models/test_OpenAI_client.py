import pytest
from PAI.models.OpenAI_client import OpenAIClient


def test_OpenAI_client_init_1():
    """Test initialization with API key provided as parameter"""
    client = OpenAIClient(api_key="test-key", model="gpt-4")
    assert client.api_key == "test-key"
    assert client.model == "gpt-4"


def test_OpenAI_client_init_2(monkeypatch):
    """Test initialization with API key from environment variable"""
    monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")
    client = OpenAIClient(model="gpt-4")
    assert client.api_key == "env-test-key"
    assert client.model == "gpt-4"


def test_OpenAI_client_generate_1(mocker):
    """Test generate method returns expected response"""

    class MockResponse:
        class MockChoice:
            class MockMessage:
                content = "Test response"

            message = MockMessage()

        choices = [MockChoice()]

    mock_create = mocker.patch("openai.resources.chat.Completions.create")
    mock_create.return_value = MockResponse()

    client = OpenAIClient(api_key="test-key")
    result = client.generate("Test prompt")

    assert result == "Test response"


def test_OpenAI_client_generate_2():
    """Test error handling for empty prompts"""
    client = OpenAIClient(api_key="test-key")
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.generate("   ")
