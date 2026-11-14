from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from .common import Money, TotalMoney


class StockEntryItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_cost: Money


class StockEntryIn(BaseModel):
    supplier_id: int = Field(gt=0)
    items: list[StockEntryItemIn] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_products(self) -> Self:
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Un produit ne peut apparaître qu'une fois.")
        return self


class StockEntryOut(BaseModel):
    id: int
    reference: str
    supplier_id: int
    total_amount: TotalMoney
    created_at: datetime
    items: list[StockEntryItemIn]


class StockLevelOut(BaseModel):
    product_id: int
    sku: str
    name: str
    quantity: int
    min_quantity: int
    status: Literal["OK", "LOW", "OUT"]


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    movement_type: Literal["IN", "OUT"]
    quantity: int
    reference: str
    note: str | None
    created_at: datetime