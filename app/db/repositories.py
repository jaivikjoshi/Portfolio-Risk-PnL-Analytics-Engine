from __future__ import annotations

from datetime import date

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

from app.db.models import (
    BenchmarkPrice,
    FxRate,
    IngestionBatch,
    Instrument,
    Portfolio,
    PortfolioDailySnapshot,
    Price,
    Trade,
    ValidationIssue,
)


def get_portfolio(db: Session, portfolio_id: str) -> Portfolio | None:
    return db.scalar(select(Portfolio).where(Portfolio.portfolio_id == portfolio_id))


def list_trades(
    db: Session,
    portfolio_id: str | None = None,
    end_date: date | None = None,
) -> list[Trade]:
    stmt: Select[tuple[Trade]] = select(Trade)
    if portfolio_id:
        stmt = stmt.where(Trade.portfolio_id == portfolio_id)
    if end_date:
        stmt = stmt.where(Trade.trade_date <= end_date)
    stmt = stmt.order_by(Trade.trade_date.asc(), Trade.trade_id.asc())
    return list(db.scalars(stmt))


def list_prices(db: Session, end_date: date | None = None) -> list[Price]:
    stmt: Select[tuple[Price]] = select(Price)
    if end_date:
        stmt = stmt.where(Price.price_date <= end_date)
    stmt = stmt.order_by(Price.instrument_id.asc(), Price.price_date.asc())
    return list(db.scalars(stmt))


def list_fx_rates(db: Session, end_date: date | None = None) -> list[FxRate]:
    stmt: Select[tuple[FxRate]] = select(FxRate)
    if end_date:
        stmt = stmt.where(FxRate.rate_date <= end_date)
    stmt = stmt.order_by(FxRate.from_currency.asc(), FxRate.to_currency.asc(), FxRate.rate_date.asc())
    return list(db.scalars(stmt))


def list_benchmark_prices(
    db: Session, benchmark_id: str, start_date: date, end_date: date
) -> list[BenchmarkPrice]:
    stmt = (
        select(BenchmarkPrice)
        .where(
            BenchmarkPrice.benchmark_id == benchmark_id,
            BenchmarkPrice.price_date >= start_date,
            BenchmarkPrice.price_date <= end_date,
        )
        .order_by(BenchmarkPrice.price_date.asc())
    )
    return list(db.scalars(stmt))


def upsert_snapshot(db: Session, snapshot: PortfolioDailySnapshot) -> PortfolioDailySnapshot:
    existing = db.scalar(
        select(PortfolioDailySnapshot).where(
            PortfolioDailySnapshot.portfolio_id == snapshot.portfolio_id,
            PortfolioDailySnapshot.snapshot_date == snapshot.snapshot_date,
        )
    )
    if existing:
        existing.market_value = snapshot.market_value
        existing.daily_return = snapshot.daily_return
        existing.cumulative_return = snapshot.cumulative_return
        existing.positions_count = snapshot.positions_count
        existing.base_currency = snapshot.base_currency
        return existing
    db.add(snapshot)
    return snapshot


def list_instruments(db: Session) -> list[Instrument]:
    return list(db.scalars(select(Instrument).order_by(Instrument.instrument_id.asc())))


def list_portfolios(db: Session) -> list[Portfolio]:
    return list(db.scalars(select(Portfolio).order_by(Portfolio.portfolio_id.asc())))


def get_latest_price(db: Session, instrument_id: str, as_of: date) -> Price | None:
    return db.scalar(
        select(Price)
        .where(Price.instrument_id == instrument_id, Price.price_date <= as_of)
        .order_by(Price.price_date.desc())
        .limit(1)
    )


def existing_batch_by_hash(db: Session, source_hash: str) -> IngestionBatch | None:
    return db.scalar(select(IngestionBatch).where(IngestionBatch.source_hash == source_hash))


def add_issue(
    db: Session,
    *,
    issue_id: str,
    batch_id: str | None,
    severity: str,
    entity_type: str,
    entity_id: str,
    rule_code: str,
    message: str,
    source_file: str | None = None,
    source_row: int | None = None,
) -> ValidationIssue:
    issue = ValidationIssue(
        issue_id=issue_id,
        batch_id=batch_id,
        severity=severity,
        entity_type=entity_type,
        entity_id=entity_id,
        rule_code=rule_code,
        message=message,
        source_file=source_file,
        source_row=source_row,
    )
    db.add(issue)
    return issue


def clear_validation_issues(db: Session) -> None:
    db.execute(delete(ValidationIssue))
