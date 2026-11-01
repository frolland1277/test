"""Shared fixtures: every test gets a fresh SQLite database file."""
import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # get_connection() reads db.DB_PATH on each call, so pointing it at a
    # temp file isolates each test from app.db and from the other tests.
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    # Entering the context runs the startup hook, which creates the schema.
    with TestClient(app) as c:
        yield c


@pytest.fixture
def customer_type(client):
    return client.post("/customer-types", json={"name": "retail"}).json()


@pytest.fixture
def product(client):
    return client.post("/products", json={"name": "Widget", "sku": "W-1"}).json()


@pytest.fixture
def customer(client, customer_type):
    return client.post(
        "/customers", json={"name": "Acme", "customer_type_id": customer_type["id"]}
    ).json()
