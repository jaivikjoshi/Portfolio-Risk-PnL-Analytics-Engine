from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class BenchmarkPointOut(BaseModel):
    date: date
    portfolio_cumulative_return: float
    benchmark_cumulative_return: float
    active_return: float


class BenchmarkComparisonResponse(BaseModel):
    portfolio_id: str
    benchmark_id: str
    start_date: date
    end_date: date
    observations: int
    ending_active_return: float | None
    series: list[BenchmarkPointOut]

