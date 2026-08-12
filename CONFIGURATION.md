# Configuration Guide

## Overview

All important configuration variables are now loaded from `secrets.toml` (for Streamlit Cloud) or `.env` (for local development). **No input fields in the app** - configuration is read-only and must be set before deployment.

## Configuration Variables

- `openai_api_key` - Your OpenAI API key
- `openai_url` - OpenAI API endpoint 
- `model_name` - LLM model name 
- `model_version` - API version

## Local Development Setup

### Option 1: Using `.env` file (Recommended for Local Development)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your values to below keys:
```
OPENAI_API_KEY = your-api-key-here
OPENAI_URL = your-api-URL-here
MODEL_NAME = your-model-name-here
MODEL_VERSION = your-model-version-here
```

3. Run the app:
```bash
streamlit run app.py
```

### Option 2: Using Streamlit Secrets (For Local Testing)

1. Edit `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = your-api-key-here
OPENAI_URL = your-api-URL-here
MODEL_NAME = your-model-name-here
MODEL_VERSION = your-model-version-here
```

2. Run the app:
```bash
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Push your code to GitHub (make sure `.env` and `.streamlit/secrets.toml` are in `.gitignore`)

2. Deploy on Streamlit Cloud:
   - Go to https://streamlit.io/cloud
   - Connect your GitHub repository
   - Select `app.py` as the main file

3. Add secrets in Streamlit Cloud:
   - In your app settings → Secrets
   - Add each variable:
   ```
   OPENAI_API_KEY = your-api-key-here
   OPENAI_URL = your-api-URL-here
   MODEL_NAME = your-model-name-here
   MODEL_VERSION = your-model-version-here
   ```

## How It Works

The `Settings` class in `config.py`:

1. **On startup**: Checks if running in Streamlit or local environment
2. **Loads from environment**:
   - `.env` file (local development)
   - Environment variables
3. **Then loads from secrets**:
   - `.streamlit/secrets.toml` (Streamlit Cloud or local)
   - Streamlit's built-in secrets support

Priority: Direct parameters → Environment variables → `.env` → Streamlit secrets

## Testing

Tests automatically disable `.env` loading to prevent conflicts. Run tests with:

```bash
pytest tests/ -v
```

Configuration is properly isolated during testing using the `PYTEST_CURRENT_TEST` environment variable.
