from __future__ import annotations

from datetime import date

from app.analytics.exposures import compute_exposures
from app.analytics.pnl import compute_pnl
from app.analytics.positions import compute_position_states
from app.analytics.returns import compute_returns
from app.analytics.risk import compute_risk_metrics


def _golden_inputs():
    instruments = {
        "I_AAPL": {
            "instrument_id": "I_AAPL",
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "asset_class": "Equity",
            "sector": "Technology",
            "currency": "USD",
            "exchange": "NASDAQ",
        }
    }
    trades = [
        {
            "trade_id": "T_001",
            "portfolio_id": "P_MAIN",
            "instrument_id": "I_AAPL",
            "trade_date": date(2026, 1, 2),
            "side": "BUY",
            "quantity": 100,
            "price": 10.0,
            "fees": 1.0,
            "currency": "USD",
        },
        {
            "trade_id": "T_002",
            "portfolio_id": "P_MAIN",
            "instrument_id": "I_AAPL",
            "trade_date": date(2026, 1, 3),
            "side": "BUY",
            "quantity": 50,
            "price": 12.0,
            "fees": 1.0,
            "currency": "USD",
        },
        {
            "trade_id": "T_003",
            "portfolio_id": "P_MAIN",
            "instrument_id": "I_AAPL",
            "trade_date": date(2026, 1, 5),
            "side": "SELL",
            "quantity": 80,
            "price": 15.0,
            "fees": 1.0,
            "currency": "USD",
        },
    ]
    prices = [{"instrument_id": "I_AAPL", "price_date": date(2026, 1, 10), "close_price": 14.0, "currency": "USD"}]
    return trades, prices, instruments


def test_weighted_average_positions_and_unrealized_pnl():
    trades, prices, instruments = _golden_inputs()
    positions = compute_position_states(trades, prices, instruments, as_of=date(2026, 1, 10))

    assert len(positions) == 1
    assert positions[0]["quantity"] == 70
    assert positions[0]["average_cost"] == 10.68
    assert positions[0]["cost_basis"] == 747.6
    assert positions[0]["market_value"] == 980.0
    assert positions[0]["unrealized_pnl"] == 232.4


def test_realized_unrealized_and_total_pnl():
    trades, prices, instruments = _golden_inputs()
    pnl = compute_pnl(
        trades,
        prices,
        instruments,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 10),
    )

    assert pnl["realized_pnl"] == 344.6
    assert pnl["unrealized_pnl"] == 232.4
    assert pnl["total_pnl"] == 577.0


def test_exposure_groups_sum_to_one_for_single_position():
    trades, prices, instruments = _golden_inputs()
    exposures = compute_exposures(
        trades,
        prices,
        instruments,
        as_of=date(2026, 1, 10),
        group_by="sector",
    )

    assert exposures["total_market_value"] == 980.0
    assert exposures["exposures"][0]["group"] == "Technology"
    assert exposures["exposures"][0]["exposure_percentage"] == 1.0


def test_returns_and_risk_metrics_are_computed():
    trades, _, instruments = _golden_inputs()
    prices = [
        {"instrument_id": "I_AAPL", "price_date": date(2026, 1, 2), "close_price": 10.0, "currency": "USD"},
        {"instrument_id": "I_AAPL", "price_date": date(2026, 1, 3), "close_price": 12.0, "currency": "USD"},
        {"instrument_id": "I_AAPL", "price_date": date(2026, 1, 4), "close_price": 13.0, "currency": "USD"},
        {"instrument_id": "I_AAPL", "price_date": date(2026, 1, 5), "close_price": 15.0, "currency": "USD"},
        {"instrument_id": "I_AAPL", "price_date": date(2026, 1, 6), "close_price": 14.0, "currency": "USD"},
    ]

    returns = compute_returns(
        trades,
        prices,
        instruments,
        start_date=date(2026, 1, 2),
        end_date=date(2026, 1, 6),
    )
    risk = compute_risk_metrics(returns)

    assert len(returns) == 5
    assert returns[-1]["market_value"] == 980.0
    assert risk["observations"] >= 2
    assert risk["annualized_volatility"] is not None

