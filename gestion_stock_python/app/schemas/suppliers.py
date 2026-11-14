from pydantic import BaseModel, ConfigDict, Field


class SupplierIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    address: str | None = Field(default=None, max_length=255)


class SupplierOut(SupplierIn):
    model_config = ConfigDict(from_attributes=True)

    id: int