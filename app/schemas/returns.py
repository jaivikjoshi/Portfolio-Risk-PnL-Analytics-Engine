from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DailyReturnOut(BaseModel):
    date: date
    market_value: float
    daily_return: float | None
    cumulative_return: float


class ReturnsResponse(BaseModel):
    portfolio_id: str
    start_date: date
    end_date: date
    returns: list[DailyReturnOut]

