from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class InstrumentPnlOut(BaseModel):
    instrument_id: str
    ticker: str
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float


class PnlResponse(BaseModel):
    portfolio_id: str
    start_date: date
    end_date: date
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    by_instrument: list[InstrumentPnlOut]

