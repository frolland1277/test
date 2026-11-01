"""Soft delete behaviour: deleted rows are flagged, hidden, and free their unique values."""
import sqlite3

import pytest

from app import db


def raw_row(table, row_id):
    """Read a row straight from SQLite, bypassing the API's deleted filter."""
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# (resource path, table, payload builder taking the fixtures dict)
RESOURCES = [
    ("products", "products", lambda f: {"name": "Gadget", "sku": "G-1"}),
    ("stock", "stock", lambda f: {"product_id": f["product"]["id"], "quantity": 5}),
    ("customer-types", "customer_type", lambda f: {"name": "wholesale"}),
    (
        "customers",
        "customer",
        lambda f: {"name": "Globex", "customer_type_id": f["customer_type"]["id"]},
    ),
    (
        "product-pricing",
        "product_pricing",
        lambda f: {
            "product_id": f["product"]["id"],
            "customer_id": f["customer"]["id"],
            "discount": 10,
            "valid_from": "2026-01-01",
        },
    ),
]


@pytest.fixture
def deps(product, customer_type, customer):
    return {"product": product, "customer_type": customer_type, "customer": customer}


# --- delete marks rows deleted and hides them --------------------------------


@pytest.mark.parametrize("resource,table,payload", RESOURCES, ids=[r[0] for r in RESOURCES])
def test_delete_flags_row_and_hides_it(client, deps, resource, table, payload):
    created = client.post(f"/{resource}", json=payload(deps))
    assert created.status_code == 201
    row_id = created.json()["id"]
    assert created.json()["deleted"] == 0

    assert client.delete(f"/{resource}/{row_id}").status_code == 204

    # The row is still in the table, flagged as deleted.
    row = raw_row(table, row_id)
    assert row is not None
    assert row["deleted"] == 1

    # ...but the API no longer returns it.
    assert client.get(f"/{resource}/{row_id}").status_code == 404
    assert row_id not in [r["id"] for r in client.get(f"/{resource}").json()]


def test_delete_leaves_other_rows_visible(client):
    a = client.post("/customer-types", json={"name": "a"}).json()
    b = client.post("/customer-types", json={"name": "b"}).json()

    client.delete(f"/customer-types/{a['id']}")

    assert [r["id"] for r in client.get("/customer-types").json()] == [b["id"]]
    assert client.get(f"/customer-types/{b['id']}").status_code == 200


def test_delete_twice_returns_404(client, customer_type):
    path = f"/customer-types/{customer_type['id']}"
    assert client.delete(path).status_code == 204
    assert client.delete(path).status_code == 404


def test_delete_missing_row_returns_404(client):
    assert client.delete("/customer-types/999").status_code == 404


# --- unique values among active rows -----------------------------------------

# (resource path, payload builder) for each partial unique index in schema.sql
UNIQUE_CASES = [
    ("products", lambda f: {"name": "Gadget", "sku": "DUP-1"}),
    ("customer-types", lambda f: {"name": "vip"}),
    (
        "product-pricing",
        lambda f: {
            "product_id": f["product"]["id"],
            "customer_id": f["customer"]["id"],
            "discount": 5,
            "valid_from": "2026-06-01",
        },
    ),
]
UNIQUE_IDS = [c[0] for c in UNIQUE_CASES]


@pytest.mark.parametrize("resource,payload", UNIQUE_CASES, ids=UNIQUE_IDS)
def test_duplicate_among_active_rows_rejected(client, deps, resource, payload):
    assert client.post(f"/{resource}", json=payload(deps)).status_code == 201

    dup = client.post(f"/{resource}", json=payload(deps))

    assert dup.status_code == 400
    assert "UNIQUE constraint failed" in dup.json()["detail"]


@pytest.mark.parametrize("resource,payload", UNIQUE_CASES, ids=UNIQUE_IDS)
def test_same_value_accepted_after_soft_delete(client, deps, resource, payload):
    first = client.post(f"/{resource}", json=payload(deps)).json()
    assert client.delete(f"/{resource}/{first['id']}").status_code == 204

    again = client.post(f"/{resource}", json=payload(deps))

    assert again.status_code == 201
    assert again.json()["id"] != first["id"]
    # The new row is visible, the deleted one is not.
    visible = [r["id"] for r in client.get(f"/{resource}").json()]
    assert again.json()["id"] in visible
    assert first["id"] not in visible


def test_value_reusable_across_several_delete_cycles(client):
    ids = []
    for _ in range(3):
        created = client.post("/customer-types", json={"name": "seasonal"})
        assert created.status_code == 201
        ids.append(created.json()["id"])
        client.delete(f"/customer-types/{ids[-1]}")

    # All three versions are kept as deleted history.
    assert all(raw_row("customer_type", i)["deleted"] == 1 for i in ids)
    # And there is still room for one active row, but only one.
    assert client.post("/customer-types", json={"name": "seasonal"}).status_code == 201
    assert client.post("/customer-types", json={"name": "seasonal"}).status_code == 400
