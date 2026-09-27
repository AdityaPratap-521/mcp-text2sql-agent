import os
import sys
import pytest

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(autouse=True)
def set_testing_env():
    """Ensure tests run cleanly using mock/standalone settings."""
    os.environ["ANTHROPIC_MODEL"] = "mock"
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["AUTO_UAT_APPROVAL"] = "true"
