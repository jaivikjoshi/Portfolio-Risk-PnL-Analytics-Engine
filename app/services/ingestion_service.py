from __future__ import annotations

import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import IngestionBatch, Instrument, Portfolio, Price, Trade
from app.db.repositories import add_issue, existing_batch_by_hash
from app.schemas.ingestion import IngestionResult
from app.utils.dates import parse_date
from app.utils.hashing import sha256_bytes, sha256_file


REQUIRED_COLUMNS = {
    "portfolios": {"portfolio_id", "portfolio_name", "base_currency", "created_at"},
    "instruments": {
        "instrument_id",
        "ticker",
        "name",
        "asset_class",
        "sector",
        "currency",
        "exchange",
    },
    "trades": {
        "trade_id",
        "portfolio_id",
        "instrument_id",
        "trade_date",
        "side",
        "quantity",
        "price",
        "fees",
        "currency",
    },
    "prices": {"instrument_id", "price_date", "close_price", "currency"},
}


@dataclass(frozen=True)
class RowIssue:
    severity: str
    entity_type: str
    entity_id: str
    rule_code: str
    message: str
    source_row: int | None


def _batch_id(source_type: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"BATCH_{source_type.upper()}_{stamp}_{uuid4().hex[:8]}"


def _clean_currency(value: Any) -> str:
    return str(value).strip().upper()


def _clean_string(value: Any) -> str:
    return "" if pd.isna(value) else str(value).strip()


def _positive_float(value: Any) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise ValueError("value must be positive")
    return parsed


def _non_negative_float(value: Any) -> float:
    parsed = float(value)
    if parsed < 0:
        raise ValueError("value must be non-negative")
    return parsed


def _issue_id(batch_id: str, rule_code: str, source_row: int | None, entity_id: str) -> str:
    row = "file" if source_row is None else str(source_row)
    return f"{batch_id}:{rule_code}:{row}:{entity_id}"


def _validate_columns(
    df: pd.DataFrame, source_type: str, batch_id: str
) -> list[RowIssue]:
    missing = sorted(REQUIRED_COLUMNS[source_type] - set(df.columns))
    if not missing:
        return []
    return [
        RowIssue(
            severity="CRITICAL",
            entity_type=source_type,
            entity_id=source_type,
            rule_code="MISSING_COLUMNS",
            message=f"Missing required columns: {', '.join(missing)}",
            source_row=None,
        )
    ]


def _portfolio_from_row(row: pd.Series) -> Portfolio:
    return Portfolio(
        portfolio_id=_clean_string(row["portfolio_id"]),
        name=_clean_string(row["portfolio_name"]),
        base_currency=_clean_currency(row["base_currency"]),
    )


def _instrument_from_row(row: pd.Series) -> Instrument:
    return Instrument(
        instrument_id=_clean_string(row["instrument_id"]),
        ticker=_clean_string(row["ticker"]).upper(),
        name=_clean_string(row["name"]),
        asset_class=_clean_string(row["asset_class"]),
        sector=_clean_string(row["sector"]) or "Unknown",
        currency=_clean_currency(row["currency"]),
        exchange=_clean_string(row["exchange"]),
    )


def _trade_from_row(row: pd.Series, batch_id: str) -> Trade:
    side = _clean_string(row["side"]).upper()
    if side not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL")
    return Trade(
        trade_id=_clean_string(row["trade_id"]),
        portfolio_id=_clean_string(row["portfolio_id"]),
        instrument_id=_clean_string(row["instrument_id"]),
        trade_date=parse_date(row["trade_date"]),
        side=side,
        quantity=_positive_float(row["quantity"]),
        price=_positive_float(row["price"]),
        fees=_non_negative_float(row["fees"]),
        currency=_clean_currency(row["currency"]),
        batch_id=batch_id,
    )


def _price_from_row(row: pd.Series, batch_id: str) -> Price:
    return Price(
        instrument_id=_clean_string(row["instrument_id"]),
        price_date=parse_date(row["price_date"]),
        close_price=_positive_float(row["close_price"]),
        currency=_clean_currency(row["currency"]),
        batch_id=batch_id,
    )


def _object_from_row(source_type: str, row: pd.Series, batch_id: str) -> object:
    if source_type == "portfolios":
        return _portfolio_from_row(row)
    if source_type == "instruments":
        return _instrument_from_row(row)
    if source_type == "trades":
        return _trade_from_row(row, batch_id)
    if source_type == "prices":
        return _price_from_row(row, batch_id)
    raise ValueError(f"Unsupported source_type: {source_type}")


def ingest_dataframe(
    db: Session,
    *,
    source_type: str,
    df: pd.DataFrame,
    source_file: str,
    source_hash: str,
    force: bool = False,
) -> IngestionResult:
    if source_type not in REQUIRED_COLUMNS:
        raise ValueError(f"Unsupported source_type: {source_type}")

    if not force and existing_batch_by_hash(db, source_hash):
        raise ValueError(f"Source file '{source_file}' was already ingested.")

    batch_id = _batch_id(source_type)
    batch = IngestionBatch(
        batch_id=batch_id,
        source_type=source_type,
        source_file=source_file,
        source_hash=source_hash,
        rows_received=len(df),
        status="started",
    )
    db.add(batch)
    db.flush()

    issues = _validate_columns(df, source_type, batch_id)
    loaded = 0
    rejected = 0

    if not issues:
        for idx, row in df.iterrows():
            source_row = int(idx) + 2
            try:
                db.add(_object_from_row(source_type, row, batch_id))
                db.flush()
                loaded += 1
            except (ValueError, IntegrityError) as exc:
                db.rollback()
                batch = db.merge(batch)
                rejected += 1
                issues.append(
                    RowIssue(
                        severity="ERROR",
                        entity_type=source_type,
                        entity_id=_clean_string(
                            row.get("trade_id")
                            or row.get("instrument_id")
                            or row.get("portfolio_id")
                            or source_type
                        ),
                        rule_code="INVALID_ROW",
                        message=str(exc).splitlines()[0],
                        source_row=source_row,
                    )
                )

    for issue in issues:
        add_issue(
            db,
            issue_id=_issue_id(batch_id, issue.rule_code, issue.source_row, issue.entity_id),
            batch_id=batch_id,
            severity=issue.severity,
            entity_type=issue.entity_type,
            entity_id=issue.entity_id,
            rule_code=issue.rule_code,
            message=issue.message,
            source_file=source_file,
            source_row=issue.source_row,
        )

    batch.rows_loaded = loaded
    batch.rows_rejected = rejected + len([i for i in issues if i.source_row is None])
    batch.status = "failed" if any(i.severity == "CRITICAL" for i in issues) else "completed"
    batch.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    return IngestionResult(
        batch_id=batch.batch_id,
        status=batch.status,
        source_type=source_type,
        rows_received=batch.rows_received,
        rows_loaded=batch.rows_loaded,
        rows_rejected=batch.rows_rejected,
        issues_count=len(issues),
    )


def ingest_csv_path(
    db: Session, *, source_type: str, path: str | Path, force: bool = False
) -> IngestionResult:
    path = Path(path)
    df = pd.read_csv(path)
    return ingest_dataframe(
        db,
        source_type=source_type,
        df=df,
        source_file=str(path),
        source_hash=sha256_file(path),
        force=force,
    )


async def ingest_upload(
    db: Session, *, source_type: str, filename: str, content: bytes, force: bool = False
) -> IngestionResult:
    with tempfile.NamedTemporaryFile(suffix=".csv") as tmp:
        tmp.write(content)
        tmp.flush()
        df = pd.read_csv(tmp.name)
    return ingest_dataframe(
        db,
        source_type=source_type,
        df=df,
        source_file=filename,
        source_hash=sha256_bytes(content),
        force=force,
    )


def seed_sample_data(db: Session, *, force: bool = True) -> list[IngestionResult]:
    base = Path("data/sample")
    ordered_sources = [
        ("portfolios", base / "portfolios.csv"),
        ("instruments", base / "instruments.csv"),
        ("trades", base / "trades.csv"),
        ("prices", base / "prices.csv"),
    ]
    return [ingest_csv_path(db, source_type=source, path=path, force=force) for source, path in ordered_sources]

