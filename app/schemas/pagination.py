from __future__ import annotations
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")

class PageMeta(BaseModel):
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)

class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)
    items: List[T]
    meta: PageMeta
