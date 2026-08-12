"""Configuration management for JD To Resume Customiser."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Only load .env in non-test environments
if os.getenv("PYTEST_CURRENT_TEST") is None:
    load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from secrets.toml and environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("PYTEST_CURRENT_TEST") is None else None,
        case_sensitive=False
    )

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4-turbo-preview"
    model_version: str = "2024-04-09"

    def __init__(self, **data):
        """Initialize settings with Streamlit secrets support if available."""
        super().__init__(**data)
        # Try to load from Streamlit secrets if running in Streamlit (not in tests)
        if os.getenv("PYTEST_CURRENT_TEST") is None:
            self._load_streamlit_secrets()

    def _load_streamlit_secrets(self):
        """Load settings from Streamlit secrets.toml if available."""
        try:
            import streamlit as st
            secrets = st.secrets
            
            if "openai_api_key" in secrets:
                self.openai_api_key = secrets["openai_api_key"]
            if "openai_url" in secrets:
                self.openai_url = secrets["openai_url"]
            if "model_name" in secrets:
                self.model_name = secrets["model_name"]
            if "model_version" in secrets:
                self.model_version = secrets["model_version"]
        except (ImportError, AttributeError, KeyError, FileNotFoundError):
            # Not running in Streamlit or secrets not available
            pass

    def validate_api_keys(self) -> bool:
        """Validate that the required API key is present."""
        return bool(self.openai_api_key)

    @property
    def api_key(self) -> str:
        """Get the configured OpenAI API key."""
        return self.openai_api_key


settings = Settings()
