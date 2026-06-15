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
