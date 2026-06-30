from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class PositionOut(BaseModel):
    instrument_id: str
    ticker: str
    name: str
    asset_class: str
    sector: str
    currency: str
    quantity: float
    average_cost: float
    cost_basis: float
    market_price: float
    market_value: float
    unrealized_pnl: float


class PositionsResponse(BaseModel):
    portfolio_id: str
    as_of: date
    positions: list[PositionOut]

