from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Instrument, Price, Trade, ValidationIssue
from app.db.repositories import add_issue, clear_validation_issues, list_prices, list_trades


def _issue_id(rule: str, entity_type: str, entity_id: str) -> str:
    return f"RUN:{rule}:{entity_type}:{entity_id}"


def _add_run_issue(
    db: Session,
    *,
    severity: str,
    entity_type: str,
    entity_id: str,
    rule_code: str,
    message: str,
) -> None:
    add_issue(
        db,
        issue_id=_issue_id(rule_code, entity_type, entity_id),
        batch_id=None,
        severity=severity,
        entity_type=entity_type,
        entity_id=entity_id,
        rule_code=rule_code,
        message=message,
    )


def run_validation(db: Session) -> dict[str, int | str]:
    clear_validation_issues(db)
    issues_created = 0

    instrument_ids = {row[0] for row in db.execute(select(Instrument.instrument_id)).all()}
    price_instruments = {row[0] for row in db.execute(select(Price.instrument_id).distinct()).all()}

    duplicate_trade_ids = db.execute(
        select(Trade.trade_id).group_by(Trade.trade_id).having(func.count(Trade.id) > 1)
    ).all()
    for (trade_id,) in duplicate_trade_ids:
        _add_run_issue(
            db,
            severity="ERROR",
            entity_type="trade",
            entity_id=trade_id,
            rule_code="DUPLICATE_TRADE_ID",
            message=f"Trade ID {trade_id} appears more than once.",
        )
        issues_created += 1

    for trade in list_trades(db):
        if trade.quantity <= 0 or trade.price <= 0 or trade.fees < 0:
            _add_run_issue(
                db,
                severity="ERROR",
                entity_type="trade",
                entity_id=trade.trade_id,
                rule_code="INVALID_TRADE_VALUES",
                message="Trade quantity and price must be positive and fees must be non-negative.",
            )
            issues_created += 1
        if trade.instrument_id not in instrument_ids:
            _add_run_issue(
                db,
                severity="CRITICAL",
                entity_type="trade",
                entity_id=trade.trade_id,
                rule_code="UNKNOWN_INSTRUMENT",
                message=f"Trade references unknown instrument {trade.instrument_id}.",
            )
            issues_created += 1

    for instrument_id in sorted(instrument_ids - price_instruments):
        _add_run_issue(
            db,
            severity="ERROR",
            entity_type="instrument",
            entity_id=instrument_id,
            rule_code="MISSING_PRICE",
            message=f"No prices loaded for instrument {instrument_id}.",
        )
        issues_created += 1

    latest_price_date = db.scalar(select(func.max(Price.price_date)))
    if latest_price_date:
        issues_created += _check_missing_prices_for_open_positions(db, latest_price_date)

    issues_created += _check_sell_quantity_breaks(db)
    db.commit()

    counts = {
        "CRITICAL": db.scalar(
            select(func.count()).select_from(ValidationIssue).where(ValidationIssue.severity == "CRITICAL")
        )
        or 0,
        "ERROR": db.scalar(
            select(func.count()).select_from(ValidationIssue).where(ValidationIssue.severity == "ERROR")
        )
        or 0,
        "WARNING": db.scalar(
            select(func.count()).select_from(ValidationIssue).where(ValidationIssue.severity == "WARNING")
        )
        or 0,
    }
    return {
        "status": "completed",
        "issues_created": issues_created,
        "critical_count": int(counts["CRITICAL"]),
        "error_count": int(counts["ERROR"]),
        "warning_count": int(counts["WARNING"]),
    }


def _check_missing_prices_for_open_positions(db: Session, as_of: date) -> int:
    prices = list_prices(db, end_date=as_of)
    priced_instruments = {price.instrument_id for price in prices if price.price_date <= as_of}
    quantities: dict[str, float] = defaultdict(float)

    for trade in list_trades(db, end_date=as_of):
        quantities[trade.instrument_id] += trade.quantity if trade.side == "BUY" else -trade.quantity

    count = 0
    for instrument_id, quantity in quantities.items():
        if abs(quantity) > 1e-9 and instrument_id not in priced_instruments:
            _add_run_issue(
                db,
                severity="ERROR",
                entity_type="instrument",
                entity_id=instrument_id,
                rule_code="MISSING_PRICE",
                message=f"Open position in {instrument_id} has no available price on or before {as_of}.",
            )
            count += 1
    return count


def _check_sell_quantity_breaks(db: Session) -> int:
    quantities: dict[tuple[str, str], float] = defaultdict(float)
    count = 0
    for trade in list_trades(db):
        key = (trade.portfolio_id, trade.instrument_id)
        if trade.side == "BUY":
            quantities[key] += trade.quantity
            continue
        if trade.quantity > quantities[key]:
            _add_run_issue(
                db,
                severity="CRITICAL",
                entity_type="trade",
                entity_id=trade.trade_id,
                rule_code="SELL_EXCEEDS_POSITION",
                message=(
                    f"Sell trade {trade.trade_id} exceeds available quantity for "
                    f"{trade.instrument_id} in {trade.portfolio_id}."
                ),
            )
            count += 1
        quantities[key] -= trade.quantity
    return count


def list_issues(
    db: Session,
    *,
    severity: str | None = None,
    rule_code: str | None = None,
    limit: int = 100,
) -> list[ValidationIssue]:
    stmt = select(ValidationIssue)
    if severity:
        stmt = stmt.where(ValidationIssue.severity == severity.upper())
    if rule_code:
        stmt = stmt.where(ValidationIssue.rule_code == rule_code.upper())
    stmt = stmt.order_by(ValidationIssue.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))

