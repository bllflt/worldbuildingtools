import pytest
from flask.testing import FlaskClient

from flaskr import create_app
from flaskr.model import db


@pytest.fixture()
def app():
    app = create_app()
    yield app


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        db.create_all()
        yield app.app_context()
        db.session.close()
        db.drop_all()
