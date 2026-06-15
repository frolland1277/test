"""Pydantic request models for each table's `add` (create) endpoint.

Only the user-supplied columns are exposed; `id`, `created_at` and
`updated_at` are managed by the database.
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    currency: str = "USD"
    is_active: bool = True


class StockCreate(BaseModel):
    product_id: int
    price: float = 0
    quantity: int = 0


class CustomerTypeCreate(BaseModel):
    name: str


class CustomerCreate(BaseModel):
    name: str
    address: Optional[str] = None
    customer_type_id: int


class ProductPricingCreate(BaseModel):
    product_id: int
    customer_id: int
    discount: float = 0
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
