from __future__ import annotations

from typing import Any

import numpy as np

from app.utils.money import round_money


def compute_risk_metrics(
    returns: list[dict[str, Any]],
    *,
    risk_free_rate: float = 0.02,
) -> dict[str, float | int | None]:
    daily_returns = np.array(
        [item["daily_return"] for item in returns if item.get("daily_return") is not None],
        dtype=float,
    )
    if len(daily_returns) < 2:
        return {
            "observations": int(len(daily_returns)),
            "annualized_volatility": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown": None,
            "var_95": None,
        }

    annualized_return = float(np.mean(daily_returns) * 252)
    annualized_volatility = float(np.std(daily_returns, ddof=1) * np.sqrt(252))
    downside = daily_returns[daily_returns < 0]
    downside_deviation = float(np.std(downside, ddof=1) * np.sqrt(252)) if len(downside) > 1 else None

    values = np.array([item["market_value"] for item in returns], dtype=float)
    peaks = np.maximum.accumulate(values)
    drawdowns = np.divide(values, peaks, out=np.ones_like(values), where=peaks != 0) - 1
    latest_value = float(values[-1]) if len(values) else 0.0

    return {
        "observations": int(len(daily_returns)),
        "annualized_volatility": round_money(annualized_volatility),
        "sharpe_ratio": round_money((annualized_return - risk_free_rate) / annualized_volatility)
        if annualized_volatility
        else None,
        "sortino_ratio": round_money((annualized_return - risk_free_rate) / downside_deviation)
        if downside_deviation
        else None,
        "max_drawdown": round_money(float(np.min(drawdowns))),
        "var_95": round_money(float(np.percentile(daily_returns, 5) * latest_value)),
    }

