from pydantic import BaseModel, ConfigDict, Field


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class CategoryOut(CategoryIn):
    model_config = ConfigDict(from_attributes=True)

    id: int