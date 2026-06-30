from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from app.analytics.positions import compute_position_states
from app.utils.money import round_money


GROUP_FIELDS = {
    "instrument": "ticker",
    "asset_class": "asset_class",
    "sector": "sector",
    "currency": "currency",
}


def compute_exposures(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    as_of: date,
    group_by: str,
    base_currency: str = "USD",
    fx_rates: list[dict[str, Any]] | None = None,
    allow_short_selling: bool = False,
) -> dict[str, Any]:
    if group_by not in GROUP_FIELDS:
        raise ValueError(f"group_by must be one of {', '.join(sorted(GROUP_FIELDS))}")

    positions = compute_position_states(
        trades,
        prices,
        instruments,
        as_of=as_of,
        base_currency=base_currency,
        fx_rates=fx_rates,
        allow_short_selling=allow_short_selling,
    )
    total_market_value = sum(position.get("market_value_base", position["market_value"]) for position in positions)
    if not positions:
        return {"total_market_value": 0.0, "exposures": []}

    field = GROUP_FIELDS[group_by]
    df = pd.DataFrame(positions)
    df["exposure_value"] = df["market_value_base"].where(
        df["market_value_base"].notna(), df["market_value"]
    )
    grouped = df.groupby(field)["exposure_value"].sum().reset_index()
    exposures = []

    for _, row in grouped.sort_values("exposure_value", ascending=False).iterrows():
        market_value = float(row["exposure_value"])
        exposures.append(
            {
                "group": str(row[field]),
                "market_value": round_money(market_value),
                "gross_exposure": round_money(abs(market_value)),
                "net_exposure": round_money(market_value),
                "exposure_percentage": round_money(
                    market_value / total_market_value if total_market_value else 0.0
                ),
            }
        )

    return {"total_market_value": round_money(total_market_value), "exposures": exposures}
