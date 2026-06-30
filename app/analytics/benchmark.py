from __future__ import annotations

from datetime import date
from typing import Any

from app.utils.money import round_money


def compute_benchmark_returns(prices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(prices, key=lambda item: item["price_date"])
    if not ordered:
        return []

    start_price = float(ordered[0]["close_price"])
    previous = None
    output = []
    for item in ordered:
        close = float(item["close_price"])
        daily_return = None if previous is None else (close - previous) / previous
        output.append(
            {
                "date": item["price_date"],
                "close_price": round_money(close),
                "daily_return": None if daily_return is None else round_money(daily_return),
                "cumulative_return": round_money((close / start_price) - 1) if start_price else 0.0,
            }
        )
        previous = close
    return output


def compare_to_benchmark(
    portfolio_returns: list[dict[str, Any]],
    benchmark_prices: list[dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    benchmark_returns = compute_benchmark_returns(benchmark_prices)
    portfolio_by_date = {item["date"]: item for item in portfolio_returns}
    benchmark_by_date = {item["date"]: item for item in benchmark_returns}
    common_dates = sorted(set(portfolio_by_date) & set(benchmark_by_date))

    observations = []
    for item_date in common_dates:
        portfolio_item = portfolio_by_date[item_date]
        benchmark_item = benchmark_by_date[item_date]
        portfolio_cumulative = float(portfolio_item["cumulative_return"])
        benchmark_cumulative = float(benchmark_item["cumulative_return"])
        observations.append(
            {
                "date": item_date,
                "portfolio_cumulative_return": round_money(portfolio_cumulative),
                "benchmark_cumulative_return": round_money(benchmark_cumulative),
                "active_return": round_money(portfolio_cumulative - benchmark_cumulative),
            }
        )

    ending_active_return = observations[-1]["active_return"] if observations else None
    return {
        "start_date": start_date,
        "end_date": end_date,
        "observations": len(observations),
        "ending_active_return": ending_active_return,
        "series": observations,
    }

