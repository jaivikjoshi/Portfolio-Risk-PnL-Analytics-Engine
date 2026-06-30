from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from pprint import pprint

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.analytics.benchmark import compare_to_benchmark
from app.db.repositories import list_benchmark_prices
from app.db.session import SessionLocal
from app.services.reporting_service import get_exposures, get_pnl, get_positions, get_risk
from app.services.snapshot_service import generate_snapshots


def main() -> None:
    init_db()
    with SessionLocal() as db:
        portfolio_id = "P_MAIN"
        as_of = date(2026, 1, 10)
        pprint({"positions": get_positions(db, portfolio_id=portfolio_id, as_of=as_of)})
        pprint(
            {
                "pnl": get_pnl(
                    db,
                    portfolio_id=portfolio_id,
                    start_date=date(2026, 1, 1),
                    end_date=as_of,
                )
            }
        )
        pprint(
            {
                "fifo_pnl": get_pnl(
                    db,
                    portfolio_id=portfolio_id,
                    start_date=date(2026, 1, 1),
                    end_date=as_of,
                    cost_method="fifo",
                )
            }
        )
        pprint({"exposures": get_exposures(db, portfolio_id=portfolio_id, as_of=as_of, group_by="sector")})
        portfolio_returns = get_risk(
            db,
            portfolio_id=portfolio_id,
            start_date=date(2026, 1, 2),
            end_date=as_of,
        )
        pprint(
            {
                "risk": portfolio_returns
            }
        )
        benchmark_prices = [
            {
                "benchmark_id": price.benchmark_id,
                "price_date": price.price_date,
                "close_price": price.close_price,
                "currency": price.currency,
            }
            for price in list_benchmark_prices(db, "SPY", date(2026, 1, 2), as_of)
        ]
        from app.services.reporting_service import get_returns

        pprint(
            {
                "benchmark": compare_to_benchmark(
                    get_returns(
                        db,
                        portfolio_id=portfolio_id,
                        start_date=date(2026, 1, 2),
                        end_date=as_of,
                    ),
                    benchmark_prices,
                    start_date=date(2026, 1, 2),
                    end_date=as_of,
                )
            }
        )
        snapshots = generate_snapshots(
            db,
            portfolio_id=portfolio_id,
            start_date=date(2026, 1, 2),
            end_date=as_of,
        )
        pprint(
            {
                "snapshots": {
                    "created": len(snapshots),
                    "latest_market_value": snapshots[-1].market_value if snapshots else None,
                    "latest_positions_count": snapshots[-1].positions_count if snapshots else None,
                }
            }
        )


if __name__ == "__main__":
    main()
