# Configuration Guide

## Overview

Configuration is always driven by environment variables - there is no manual entry in the
Streamlit sidebar. Values are supplied in order of precedence:

1. **`secrets.toml`** - for Streamlit Cloud deployments.
2. **`.env`** - for local development.
3. **Environment variables** - set directly in the shell/host.

The sidebar only displays the currently loaded endpoint/model and lets you click
**Test Connection** to confirm the credentials work.

## Configuration Variables

- `openai_api_key` - Your OpenAI API key
- `openai_url` - OpenAI API endpoint
- `model_name` - LLM model name
- `model_version` - API version

### Azure OpenAI

If `openai_url` contains `azure.com`, the app automatically switches to the Azure OpenAI
client (`AzureChatOpenAI`) instead of the plain OpenAI client, since Azure uses a different
URL shape (`/openai/deployments/{deployment}/chat/completions?api-version=...`). In this case:

- `openai_url` - the Azure resource base endpoint, e.g. `https://<resource>.openai.azure.com/`
- `model_name` - the **deployment name** (not the underlying model name), e.g. `gpt-5.4-hackathon-southcentralus`
- `model_version` - the Azure **api-version** query parameter, e.g. `2024-12-01-preview`

## Verifying Configuration In-App

1. Set `OPENAI_API_KEY`, `OPENAI_URL`, `MODEL_NAME`, and `MODEL_VERSION` via `.env`,
   `secrets.toml`, or environment variables (see below).
2. Run the app: `streamlit run app.py`
3. In the sidebar, click **Test Connection** - the app makes a minimal request to confirm
   the loaded credentials work
4. Once verified, the loaded configuration is used for every Analyze/Customise action

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