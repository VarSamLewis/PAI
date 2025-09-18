from PAI.PAI import PAI
import pytest


@pytest.fixture
def mock_provider(mocker):
    """Mock provider for testing"""
    provider = mocker.MagicMock()
    provider.generate.return_value = "Mock response"
    return provider


@pytest.fixture
def test_PAI_init_1(mock_provider, mocker):
    """Test PAI initialization with mock provider"""
    pai = PAI("Test_Session")
    pai.model_session.init = mocker.MagicMock()
    pai.model_session.provider = mock_provider
    pai.current_provider = "mock"
    pai.current_model = "mock-model"
    return pai


def test_PAI_init_2():
    """Test PAI empty/default initialization"""
    pai = PAI("Test_Session")
    assert hasattr(pai, "model_session")
    assert pai.current_provider is None
    assert pai.current_model is None
    assert pai.tool_enabled is True


def test_PAI_use_provider_1(mocker):
    """Test use_provider method with mocker"""
    pai = PAI("Test_Session")
    mock_provider = mocker.MagicMock()
    mock_provider.model = "test-model"

    mock_init = mocker.patch.object(pai.model_session, "init")
    pai.model_session.provider = mock_provider
    
    result = pai.use_provider("test-provider", model="test-model", param="value")
    
    mock_init.assert_called_once_with(
        "test-provider", model="test-model", param="value"
    )
    assert pai.current_provider == "test-provider"
    assert pai.current_model == "test-model"
    assert result is pai


def test_PAI_use_openai_1(mocker):
    """Test use_openai method"""
    pai = PAI("Test_Session")
    mock_provider = mocker.MagicMock()
    mock_provider.model = "gpt-4"

    mock_init = mocker.patch.object(pai.model_session, "init")
    pai.model_session.provider = mock_provider
    
    result = pai.use_openai(model="gpt-4", api_key="test-key")
    
    mock_init.assert_called_once_with("openai", model="gpt-4", api_key="test-key")
    assert pai.current_provider == "openai"
    assert pai.current_model == "gpt-4"
    assert result is pai
