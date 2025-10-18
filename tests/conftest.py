"""
Pytest configuration and fixtures.
"""
import pytest
from app import create_app
from config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Return authentication headers for testing."""
    return {
        'Authorization': 'Bearer test-token-12345',
        'Content-Type': 'application/json'
    }
