from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field, PlainSerializer

T = TypeVar("T")

Money = Annotated[
    Decimal,
    Field(ge=0, max_digits=12, decimal_places=2),
    PlainSerializer(
        lambda value: f"{value:.2f}",
        return_type=str,
        when_used="json",
    ),
]


class Meta(BaseModel):
    page: int
    limit: int
    total: int


class Page(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta