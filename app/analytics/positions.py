from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import pandas as pd

from app.analytics.fx import latest_fx_rate
from app.core.exceptions import AnalyticsError
from app.utils.money import round_money


def latest_prices_by_instrument(prices: list[dict[str, Any]], as_of: date) -> dict[str, dict[str, Any]]:
    df = pd.DataFrame(prices)
    if df.empty:
        return {}
    df = df[df["price_date"] <= as_of].sort_values(["instrument_id", "price_date"])
    if df.empty:
        return {}
    latest = df.groupby("instrument_id", as_index=False).tail(1)
    return {str(row["instrument_id"]): row.to_dict() for _, row in latest.iterrows()}


def compute_position_states(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    as_of: date,
    base_currency: str = "USD",
    fx_rates: list[dict[str, Any]] | None = None,
    allow_short_selling: bool = False,
) -> list[dict[str, Any]]:
    fx_rates = fx_rates or []
    states: dict[str, dict[str, float]] = defaultdict(
        lambda: {"quantity": 0.0, "cost_basis": 0.0, "realized_pnl": 0.0}
    )

    ordered_trades = sorted(
        [trade for trade in trades if trade["trade_date"] <= as_of],
        key=lambda t: (t["trade_date"], str(t["trade_id"])),
    )

    for trade in ordered_trades:
        instrument_id = trade["instrument_id"]
        state = states[instrument_id]
        quantity = float(trade["quantity"])
        price = float(trade["price"])
        fees = float(trade.get("fees") or 0.0)

        if trade["side"] == "BUY":
            state["quantity"] += quantity
            state["cost_basis"] += quantity * price + fees
            continue

        if trade["side"] != "SELL":
            raise AnalyticsError(f"Unsupported trade side: {trade['side']}")

        if quantity > state["quantity"] and not allow_short_selling:
            raise AnalyticsError(
                f"Sell quantity exceeds current holdings for {instrument_id} on {trade['trade_date']}."
            )

        average_cost = state["cost_basis"] / state["quantity"] if state["quantity"] else 0.0
        state["realized_pnl"] += (price - average_cost) * quantity - fees
        state["quantity"] -= quantity
        state["cost_basis"] -= average_cost * quantity

        if abs(state["quantity"]) < 1e-9:
            state["quantity"] = 0.0
            state["cost_basis"] = 0.0

    latest_prices = latest_prices_by_instrument(prices, as_of)
    positions: list[dict[str, Any]] = []

    for instrument_id, state in sorted(states.items()):
        quantity = state["quantity"]
        if abs(quantity) < 1e-9:
            continue
        instrument = instruments.get(instrument_id)
        if not instrument:
            raise AnalyticsError(f"Unknown instrument in position calculation: {instrument_id}")
        price_row = latest_prices.get(instrument_id)
        if not price_row:
            raise AnalyticsError(f"No price found for {instrument_id} on or before {as_of}.")

        average_cost = state["cost_basis"] / quantity if quantity else 0.0
        market_price = float(price_row["close_price"])
        market_value = quantity * market_price
        unrealized = (market_price - average_cost) * quantity
        fx_rate = latest_fx_rate(
            fx_rates,
            from_currency=instrument["currency"],
            to_currency=base_currency,
            as_of=as_of,
        )

        positions.append(
            {
                "instrument_id": instrument_id,
                "ticker": instrument["ticker"],
                "name": instrument["name"],
                "asset_class": instrument["asset_class"],
                "sector": instrument["sector"],
                "currency": instrument["currency"],
                "quantity": round_money(quantity),
                "average_cost": round_money(average_cost),
                "cost_basis": round_money(state["cost_basis"]),
                "market_price": round_money(market_price),
                "market_value": round_money(market_value),
                "unrealized_pnl": round_money(unrealized),
                "fx_rate": round_money(fx_rate),
                "base_currency": base_currency,
                "market_value_base": round_money(market_value * fx_rate),
                "unrealized_pnl_base": round_money(unrealized * fx_rate),
            }
        )

    return positions
