from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from .common import Money, TotalMoney


class SaleItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SaleIn(BaseModel):
    items: list[SaleItemIn] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_products(self) -> Self:
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Un produit ne peut apparaître qu'une fois par vente.")
        return self


class SaleItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Money
    subtotal: TotalMoney


class SaleOut(BaseModel):
    id: int
    reference: str
    total_amount: TotalMoney
    created_at: datetime
    items: list[SaleItemOut]