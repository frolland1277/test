# Catalog API

A small REST API (FastAPI + SQLite) exposing `add`, `select` and `delete`
operations for every table defined in [`schema.sql`](schema.sql).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

On first start the database (`app.db`) is created from `schema.sql`.
Interactive docs are available at <http://127.0.0.1:8000/docs>.

## Tests

The test suite uses pytest and FastAPI's `TestClient`. Each test runs against
its own temporary SQLite file, so your local `app.db` is never touched.

```bash
pip install -r requirements-dev.txt
pytest
```

`tests/test_soft_delete.py` covers soft delete for every resource: deleting
sets `deleted = 1` and hides the row from both `GET` endpoints, duplicates of a
unique value (`products.sku`, `customer_type.name`, and
`product_pricing (product_id, customer_id, valid_from)`) are rejected with 400
while the original row is active, and the same value is accepted again once
the original row has been soft-deleted.

Note: `pydantic==2.7.4` has no prebuilt wheel for Python 3.13, so use
Python 3.12 or earlier for the virtualenv.

## Endpoints

Each table is exposed under a resource path:

| Resource          | Table             |
| ----------------- | ----------------- |
| `/products`       | `products`        |
| `/stock`          | `stock`           |
| `/customer-types` | `customer_type`   |
| `/customers`      | `customer`        |
| `/product-pricing`| `product_pricing` |

For every resource:

| Method & path               | Description           |
| --------------------------- | --------------------- |
| `POST   /{resource}`        | add a row             |
| `GET    /{resource}`        | select all rows       |
| `GET    /{resource}/{id}`   | select a single row   |
| `DELETE /{resource}/{id}`   | soft-delete a row     |

Deletes are soft: the row's `deleted` flag is set to `1` rather than the row
being removed, and soft-deleted rows are excluded from all `select` responses.

### Example

```bash
curl -X POST localhost:8000/customer-types -H 'Content-Type: application/json' \
  -d '{"name": "wholesale"}'

curl localhost:8000/customer-types
```
