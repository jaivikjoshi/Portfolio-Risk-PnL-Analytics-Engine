from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Portfolio Risk PnL Analytics Engine")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./portfolio_engine.db")
    risk_free_rate: float = float(os.getenv("RISK_FREE_RATE", "0.02"))
    allow_short_selling: bool = _bool_env("ALLOW_SHORT_SELLING", False)
    stale_price_days: int = int(os.getenv("STALE_PRICE_DAYS", "7"))


settings = Settings()

