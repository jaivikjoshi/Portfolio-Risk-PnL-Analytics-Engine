from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.db.models import PortfolioDailySnapshot
from app.db.repositories import get_portfolio, upsert_snapshot
from app.services.reporting_service import get_positions, get_returns


def generate_snapshots(
    db: Session,
    *,
    portfolio_id: str,
    start_date: date,
    end_date: date,
) -> list[PortfolioDailySnapshot]:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        raise ValueError(f"Portfolio '{portfolio_id}' was not found.")

    returns = get_returns(db, portfolio_id=portfolio_id, start_date=start_date, end_date=end_date)
    snapshots: list[PortfolioDailySnapshot] = []
    for item in returns:
        positions = get_positions(db, portfolio_id=portfolio_id, as_of=item["date"])
        snapshot = upsert_snapshot(
            db,
            PortfolioDailySnapshot(
                portfolio_id=portfolio_id,
                snapshot_date=item["date"],
                market_value=item["market_value"],
                daily_return=item["daily_return"],
                cumulative_return=item["cumulative_return"],
                positions_count=len(positions),
                base_currency=portfolio.base_currency,
            ),
        )
        snapshots.append(snapshot)
    db.commit()
    return snapshots

