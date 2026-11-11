import pytest
from product_api.factory import create_app
from product_api.extensions import db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    application = create_app("testing")

    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

