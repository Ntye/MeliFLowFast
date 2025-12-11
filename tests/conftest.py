"""
Pytest configuration and fixtures.
"""
import pytest
from app import create_app, db
from config import TestingConfig


class TestConfigNoDb(TestingConfig):
    """Testing configuration without database."""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestConfigNoDb)
    
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            # Skip database setup if it fails (no DB available)
            pass
        yield app
        try:
            db.session.remove()
            db.drop_all()
        except Exception:
            pass


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
