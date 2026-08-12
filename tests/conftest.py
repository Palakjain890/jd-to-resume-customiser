import sys
import os
from pathlib import Path

# Ensure project root is on sys.path so tests can import top-level modules
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Pytest configuration
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment to prevent loading .env and secrets.toml files."""
    # Set environment variable to indicate we're in pytest
    original_value = os.environ.get("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "true"
    yield
    # Cleanup - restore original value or delete if it didn't exist
    if original_value is None:
        os.environ.pop("PYTEST_CURRENT_TEST", None)
    else:
        os.environ["PYTEST_CURRENT_TEST"] = original_value




