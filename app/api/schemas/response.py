from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T", bound=BaseModel)


class MetaModel(BaseModel):
    offset: int
    limit: int
    returned: int
    total: int


class ListResponse(BaseModel, Generic[T]):
    data: list[T] = Field(default_factory=list)
    meta: Optional[MetaModel] = None
