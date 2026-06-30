from __future__ import annotations


def round_money(value: float | int | None) -> float:
    return round(float(value or 0.0), 6)

