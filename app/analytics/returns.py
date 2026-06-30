from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from app.analytics.positions import compute_position_states
from app.utils.money import round_money


def compute_daily_values(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    base_currency: str = "USD",
    fx_rates: list[dict[str, Any]] | None = None,
    allow_short_selling: bool = False,
) -> list[dict[str, Any]]:
    fx_rates = fx_rates or []
    if start_date > end_date:
        return []

    values: list[dict[str, Any]] = []
    for ts in pd.date_range(start=start_date, end=end_date, freq="D"):
        as_of = ts.date()
        try:
            positions = compute_position_states(
                trades,
                prices,
                instruments,
                as_of=as_of,
                base_currency=base_currency,
                fx_rates=fx_rates,
                allow_short_selling=allow_short_selling,
            )
            market_value = sum(position.get("market_value_base", position["market_value"]) for position in positions)
        except Exception:
            market_value = 0.0
        values.append({"date": as_of, "market_value": round_money(market_value)})
    return values


def compute_returns(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    base_currency: str = "USD",
    fx_rates: list[dict[str, Any]] | None = None,
    allow_short_selling: bool = False,
) -> list[dict[str, Any]]:
    values = compute_daily_values(
        trades,
        prices,
        instruments,
        start_date=start_date,
        end_date=end_date,
        base_currency=base_currency,
        fx_rates=fx_rates,
        allow_short_selling=allow_short_selling,
    )
    if not values:
        return []

    cumulative = 1.0
    previous = None
    output: list[dict[str, Any]] = []

    for item in values:
        market_value = item["market_value"]
        daily_return = None
        if previous and previous > 0:
            daily_return = (market_value - previous) / previous
            cumulative *= 1 + daily_return
        output.append(
            {
                "date": item["date"],
                "market_value": round_money(market_value),
                "daily_return": None if daily_return is None else round_money(daily_return),
                "cumulative_return": round_money(cumulative - 1),
            }
        )
        previous = market_value

    return output
