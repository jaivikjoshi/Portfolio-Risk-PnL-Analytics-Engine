from __future__ import annotations

from datetime import date
from typing import Any


def latest_fx_rate(
    fx_rates: list[dict[str, Any]],
    *,
    from_currency: str,
    to_currency: str,
    as_of: date,
) -> float:
    source = from_currency.upper()
    target = to_currency.upper()
    if source == target:
        return 1.0

    direct = [
        rate
        for rate in fx_rates
        if rate["from_currency"] == source and rate["to_currency"] == target and rate["rate_date"] <= as_of
    ]
    if direct:
        return float(sorted(direct, key=lambda r: r["rate_date"])[-1]["rate"])

    inverse = [
        rate
        for rate in fx_rates
        if rate["from_currency"] == target and rate["to_currency"] == source and rate["rate_date"] <= as_of
    ]
    if inverse:
        return 1 / float(sorted(inverse, key=lambda r: r["rate_date"])[-1]["rate"])

    raise ValueError(f"No FX rate found from {source} to {target} on or before {as_of}.")

