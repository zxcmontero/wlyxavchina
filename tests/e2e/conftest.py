import os
import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL for E2E tests. Override with E2E_BASE_URL env var."""
    return os.getenv("E2E_BASE_URL", "http://127.0.0.1:5001")
