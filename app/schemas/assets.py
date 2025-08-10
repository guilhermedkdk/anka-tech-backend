from __future__ import annotations

from pydantic import BaseModel


class AssetSearchItem(BaseModel):
    symbol: str
    shortname: str | None = None
    longname: str | None = None
    exch: str | None = None
    exchDisp: str | None = None
    typeDisp: str | None = None
