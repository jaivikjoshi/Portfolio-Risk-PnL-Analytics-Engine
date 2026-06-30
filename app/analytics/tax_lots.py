from __future__ import annotations

from collections import defaultdict, deque
from datetime import date
from typing import Any

from app.analytics.fx import latest_fx_rate
from app.analytics.positions import latest_prices_by_instrument
from app.core.exceptions import AnalyticsError
from app.utils.money import round_money


def compute_tax_lot_pnl(
    trades: list[dict[str, Any]],
    prices: list[dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    method: str,
    base_currency: str,
    fx_rates: list[dict[str, Any]] | None = None,
    allow_short_selling: bool = False,
) -> dict[str, Any]:
    if method not in {"fifo", "lifo"}:
        raise ValueError("method must be fifo or lifo")

    lots: dict[str, deque[dict[str, float]]] = defaultdict(deque)
    realized: dict[str, float] = defaultdict(float)
    fx_rates = fx_rates or []

    ordered_trades = sorted(
        [trade for trade in trades if trade["trade_date"] <= end_date],
        key=lambda t: (t["trade_date"], str(t["trade_id"])),
    )

    for trade in ordered_trades:
        instrument_id = trade["instrument_id"]
        quantity = float(trade["quantity"])
        price = float(trade["price"])
        fees = float(trade.get("fees") or 0.0)
        instrument = instruments[instrument_id]
        fx_rate = latest_fx_rate(
            fx_rates,
            from_currency=instrument["currency"],
            to_currency=base_currency,
            as_of=trade["trade_date"],
        )

        if trade["side"] == "BUY":
            unit_cost_base = ((quantity * price) + fees) * fx_rate / quantity
            lots[instrument_id].append({"quantity": quantity, "unit_cost_base": unit_cost_base})
            continue

        if trade["side"] != "SELL":
            raise AnalyticsError(f"Unsupported trade side: {trade['side']}")

        remaining = quantity
        trade_realized = 0.0
        proceeds_per_unit_base = price * fx_rate
        while remaining > 1e-9:
            if not lots[instrument_id]:
                if allow_short_selling:
                    break
                raise AnalyticsError(
                    f"Sell quantity exceeds current holdings for {instrument_id} on {trade['trade_date']}."
                )
            lot = lots[instrument_id][0] if method == "fifo" else lots[instrument_id][-1]
            used = min(remaining, lot["quantity"])
            trade_realized += (proceeds_per_unit_base - lot["unit_cost_base"]) * used
            lot["quantity"] -= used
            remaining -= used
            if lot["quantity"] <= 1e-9:
                if method == "fifo":
                    lots[instrument_id].popleft()
                else:
                    lots[instrument_id].pop()

        trade_realized -= fees * fx_rate
        if start_date <= trade["trade_date"] <= end_date:
            realized[instrument_id] += trade_realized

    latest_prices = latest_prices_by_instrument(prices, end_date)
    by_instrument: list[dict[str, Any]] = []

    for instrument_id in sorted(set(realized) | set(lots)):
        instrument = instruments[instrument_id]
        price_row = latest_prices.get(instrument_id)
        if not price_row and lots[instrument_id]:
            raise AnalyticsError(f"No price found for {instrument_id} on or before {end_date}.")
        market_price = float(price_row["close_price"]) if price_row else 0.0
        fx_rate = latest_fx_rate(
            fx_rates,
            from_currency=instrument["currency"],
            to_currency=base_currency,
            as_of=end_date,
        )
        unrealized = 0.0
        for lot in lots[instrument_id]:
            unrealized += ((market_price * fx_rate) - lot["unit_cost_base"]) * lot["quantity"]

        realized_value = realized.get(instrument_id, 0.0)
        by_instrument.append(
            {
                "instrument_id": instrument_id,
                "ticker": instrument["ticker"],
                "realized_pnl": round_money(realized_value),
                "unrealized_pnl": round_money(unrealized),
                "total_pnl": round_money(realized_value + unrealized),
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

