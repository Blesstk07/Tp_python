from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .common import Money


class ProductIn(BaseModel):
    category_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    sku: str = Field(min_length=1, max_length=50)
    description: str | None = None
    purchase_price: Money = Decimal("0.00")
    sale_price: Money
    quantity: int = Field(default=0, ge=0)
    min_quantity: int = Field(default=0, ge=0)


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_name: str | None = None