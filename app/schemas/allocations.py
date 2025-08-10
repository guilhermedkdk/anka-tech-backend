from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Annotated

from pydantic import BaseModel, Field


# Helpers de tipo com constraints (20,8) e > 0
Decimal20_8_Pos = Annotated[Decimal, Field(gt=0, max_digits=20, decimal_places=8)]
Decimal20_8_Pos_Opt = Annotated[Optional[Decimal], Field(gt=0, max_digits=20, decimal_places=8)]


class AllocationBase(BaseModel):
    ticker: str = Field(example="VALE3.SA")
    quantity: Decimal20_8_Pos
    buy_price: Decimal20_8_Pos
    buy_date: date


class AllocationCreate(AllocationBase):
    pass


class AllocationUpdate(BaseModel):
    quantity: Decimal20_8_Pos_Opt = None
    buy_price: Decimal20_8_Pos_Opt = None
    buy_date: Optional[date] = None


class AllocationOut(BaseModel):
    id: int
    client_id: int
    ticker: str
    quantity: Decimal
    buy_price: Decimal
    buy_date: date

    class Config:
        from_attributes = True
