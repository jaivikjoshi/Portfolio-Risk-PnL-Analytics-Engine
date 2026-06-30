from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from app.analytics.positions import compute_position_states
from app.core.exceptions import AnalyticsError
from app.utils.money import round_money


def compute_realized_pnl_by_instrument(
    trades: list[dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    allow_short_selling: bool = False,
) -> dict[str, float]:
    states: dict[str, dict[str, float]] = defaultdict(
        lambda: {"quantity": 0.0, "cost_basis": 0.0}
    )
    realized: dict[str, float] = defaultdict(float)

    ordered_trades = sorted(
        [trade for trade in trades if trade["trade_date"] <= end_date],
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
        trade_realized = (price - average_cost) * quantity - fees
        if start_date <= trade["trade_date"] <= end_date:
            realized[instrument_id] += trade_realized
        state["quantity"] -= quantity
        state["cost_basis"] -= average_cost * quantity
        if abs(state["quantity"]) < 1e-9:
            state["quantity"] = 0.0
            state["cost_basis"] = 0.0

    return {instrument_id: round_money(value) for instrument_id, value in realized.items()}


def compute_pnl(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    allow_short_selling: bool = False,
) -> dict[str, Any]:
    realized = compute_realized_pnl_by_instrument(
        trades,
        start_date=start_date,
        end_date=end_date,
        allow_short_selling=allow_short_selling,
    )
    positions = compute_position_states(
        trades,
        prices,
        instruments,
        as_of=end_date,
        allow_short_selling=allow_short_selling,
    )

    by_instrument: list[dict[str, Any]] = []
    instrument_ids = sorted(set(realized) | {position["instrument_id"] for position in positions})
    position_by_id = {position["instrument_id"]: position for position in positions}

    for instrument_id in instrument_ids:
        instrument = instruments[instrument_id]
        realized_value = realized.get(instrument_id, 0.0)
        unrealized_value = position_by_id.get(instrument_id, {}).get("unrealized_pnl", 0.0)
        by_instrument.append(
            {
                "instrument_id": instrument_id,
                "ticker": instrument["ticker"],
                "realized_pnl": round_money(realized_value),
                "unrealized_pnl": round_money(unrealized_value),
                "total_pnl": round_money(realized_value + unrealized_value),
            }
        )

    total_realized = sum(item["realized_pnl"] for item in by_instrument)
    total_unrealized = sum(item["unrealized_pnl"] for item in by_instrument)
    return {
        "realized_pnl": round_money(total_realized),
        "unrealized_pnl": round_money(total_unrealized),
        "total_pnl": round_money(total_realized + total_unrealized),
        "by_instrument": by_instrument,
    }

