"""REST API exposing add / select / delete operations for each table.

For every table there are three endpoints:

    POST   /{resource}          -> add a row
    GET    /{resource}          -> select all rows
    GET    /{resource}/{id}     -> select a single row
    DELETE /{resource}/{id}     -> delete a row
"""
from typing import Type

from fastapi import FastAPI
from pydantic import BaseModel

from . import crud
from .db import init_db
from .models import (
    CustomerCreate,
    CustomerTypeCreate,
    ProductCreate,
    ProductPricingCreate,
    StockCreate,
)

app = FastAPI(title="Catalog API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


# resource path -> (database table, create model)
RESOURCES: dict[str, tuple[str, Type[BaseModel]]] = {
    "products": ("products", ProductCreate),
    "stock": ("stock", StockCreate),
    "customer-types": ("customer_type", CustomerTypeCreate),
    "customers": ("customer", CustomerCreate),
    "product-pricing": ("product_pricing", ProductPricingCreate),
}


def register_routes(resource: str, table: str, model: Type[BaseModel]) -> None:
    """Wire up add/select/delete endpoints for a single table."""

    @app.post(f"/{resource}", status_code=201, tags=[resource])
    def add(payload: model) -> dict:  # type: ignore[valid-type]
        # mode="json" keeps dates/decimals as serialisable values for sqlite.
        return crud.insert(table, payload.model_dump(mode="json"))

    @app.get(f"/{resource}", tags=[resource])
    def select_all() -> list[dict]:
        return crud.select_all(table)

    @app.get(f"/{resource}/{{row_id}}", tags=[resource])
    def select_one(row_id: int) -> dict:
        return crud.select_one(table, row_id)

    @app.delete(f"/{resource}/{{row_id}}", status_code=204, tags=[resource])
    def delete(row_id: int) -> None:
        crud.delete(table, row_id)


for _resource, (_table, _model) in RESOURCES.items():
    register_routes(_resource, _table, _model)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {"resources": list(RESOURCES.keys())}
