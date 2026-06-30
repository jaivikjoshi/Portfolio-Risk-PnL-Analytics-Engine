from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class SnapshotOut(BaseModel):
    portfolio_id: str
    snapshot_date: date
    market_value: float
    daily_return: float | None
    cumulative_return: float
    positions_count: int
    base_currency: str


class SnapshotRunResponse(BaseModel):
    portfolio_id: str
    start_date: date
    end_date: date
    snapshots_created: int
    snapshots: list[SnapshotOut]

