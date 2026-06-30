from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class ExposureOut(BaseModel):
    group: str
    market_value: float
    gross_exposure: float
    net_exposure: float
    exposure_percentage: float


class ExposuresResponse(BaseModel):
    portfolio_id: str
    as_of: date
    group_by: str
    total_market_value: float
    exposures: list[ExposureOut]

