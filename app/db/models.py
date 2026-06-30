from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    base_currency: Mapped[str] = mapped_column(String(3))

    trades: Mapped[list[Trade]] = relationship(back_populates="portfolio")


class Instrument(Base, TimestampMixin):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255))
    asset_class: Mapped[str] = mapped_column(String(64))
    sector: Mapped[str] = mapped_column(String(128), default="Unknown")
    currency: Mapped[str] = mapped_column(String(3))
    exchange: Mapped[str] = mapped_column(String(64), default="")

    trades: Mapped[list[Trade]] = relationship(back_populates="instrument")
    prices: Mapped[list[Price]] = relationship(back_populates="instrument")


class IngestionBatch(Base):
    __tablename__ = "ingestion_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(96), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    source_file: Mapped[str] = mapped_column(String(255))
    source_hash: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), default="started")
    rows_received: Mapped[int] = mapped_column(Integer, default=0)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    issues: Mapped[list[ValidationIssue]] = relationship(back_populates="batch")


class Trade(Base, TimestampMixin):
    __tablename__ = "trades"
    __table_args__ = (UniqueConstraint("trade_id", name="uq_trades_trade_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trade_id: Mapped[str] = mapped_column(String(96), index=True)
    portfolio_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("portfolios.portfolio_id"), index=True
    )
    instrument_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("instruments.instrument_id"), index=True
    )
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    side: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    fees: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3))
    batch_id: Mapped[str | None] = mapped_column(String(96), index=True, nullable=True)

    portfolio: Mapped[Portfolio] = relationship(back_populates="trades")
    instrument: Mapped[Instrument] = relationship(back_populates="trades")


class Price(Base, TimestampMixin):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("instrument_id", "price_date", name="uq_prices_instrument_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("instruments.instrument_id"), index=True
    )
    price_date: Mapped[date] = mapped_column(Date, index=True)
    close_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3))
    batch_id: Mapped[str | None] = mapped_column(String(96), index=True, nullable=True)

    instrument: Mapped[Instrument] = relationship(back_populates="prices")


class FxRate(Base, TimestampMixin):
    __tablename__ = "fx_rates"
    __table_args__ = (
        UniqueConstraint("rate_date", "from_currency", "to_currency", name="uq_fx_rate_pair_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rate_date: Mapped[date] = mapped_column(Date, index=True)
    from_currency: Mapped[str] = mapped_column(String(3), index=True)
    to_currency: Mapped[str] = mapped_column(String(3), index=True)
    rate: Mapped[float] = mapped_column(Float)
    batch_id: Mapped[str | None] = mapped_column(String(96), index=True, nullable=True)


class BenchmarkPrice(Base, TimestampMixin):
    __tablename__ = "benchmark_prices"
    __table_args__ = (
        UniqueConstraint("benchmark_id", "price_date", name="uq_benchmark_price_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benchmark_id: Mapped[str] = mapped_column(String(64), index=True)
    price_date: Mapped[date] = mapped_column(Date, index=True)
    close_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3))
    batch_id: Mapped[str | None] = mapped_column(String(96), index=True, nullable=True)


class PortfolioDailySnapshot(Base, TimestampMixin):
    __tablename__ = "portfolio_daily_snapshots"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "snapshot_date", name="uq_snapshot_portfolio_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("portfolios.portfolio_id"), index=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    market_value: Mapped[float] = mapped_column(Float)
    daily_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    cumulative_return: Mapped[float] = mapped_column(Float)
    positions_count: Mapped[int] = mapped_column(Integer)
    base_currency: Mapped[str] = mapped_column(String(3))


class ValidationIssue(Base):
    __tablename__ = "validation_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    batch_id: Mapped[str | None] = mapped_column(
        String(96), ForeignKey("ingestion_batches.batch_id"), nullable=True, index=True
    )
    severity: Mapped[str] = mapped_column(String(16), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    rule_code: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(String(1000))
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    batch: Mapped[IngestionBatch | None] = relationship(back_populates="issues")
