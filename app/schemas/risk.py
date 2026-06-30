from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class RiskResponse(BaseModel):
    portfolio_id: str
    start_date: date
    end_date: date
    observations: int
    annualized_volatility: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown: float | None
    var_95: float | None

