import pytest
from unittest.mock import patch, MagicMock
import sys
from config import Settings


def test_default_settings():
    """Test default settings without any env vars or secrets."""
    settings = Settings()
    # Should have defaults when no env vars are set
    assert settings.model_name == "gpt-4-turbo-preview"
    assert settings.model_version == "2024-04-09"
    assert settings.openai_url == "https://api.openai.com/v1"


def test_settings_from_env_vars():
    """Test settings loaded from environment variables."""
    settings = Settings(
        openai_api_key="env-key",
        model_name="gpt-4",
        model_version="2024-01-01",
        openai_url="https://custom.openai.com/v1"
    )
    assert settings.openai_api_key == "env-key"
    assert settings.model_name == "gpt-4"
    assert settings.model_version == "2024-01-01"
    assert settings.openai_url == "https://custom.openai.com/v1"


def test_validate_api_keys_present():
    """Test validation when API key is present."""
    settings = Settings(openai_api_key="test-key")
    assert settings.validate_api_keys() is True


def test_validate_api_keys_missing():
    """Test validation when API key is missing."""
    settings = Settings(openai_api_key="")
    assert settings.validate_api_keys() is False


def test_api_key_property():
    """Test the api_key property returns the correct key."""
    settings = Settings(openai_api_key="test-key")
    assert settings.api_key == "test-key"


def test_settings_all_fields_present():
    """Test that all expected configuration fields are present."""
    settings = Settings(
        openai_api_key="test-key",
        openai_url="https://test.openai.com/v1",
        model_name="gpt-4-turbo",
        model_version="2024-03-01"
    )
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "openai_url")
    assert hasattr(settings, "model_name")
    assert hasattr(settings, "model_version")
    assert settings.openai_api_key == "test-key"
    assert settings.openai_url == "https://test.openai.com/v1"
    assert settings.model_name == "gpt-4-turbo"
    assert settings.model_version == "2024-03-01"



