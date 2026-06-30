"""Add FX, benchmark, and portfolio snapshot tables.

Revision ID: 20260630_0002
Revises: 20260630_0001
Create Date: 2026-06-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260630_0002"
down_revision = "20260630_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fx_rates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("from_currency", sa.String(length=3), nullable=False),
        sa.Column("to_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rate_date", "from_currency", "to_currency", name="uq_fx_rate_pair_date"),
    )
    op.create_index("ix_fx_rates_batch_id", "fx_rates", ["batch_id"])
    op.create_index("ix_fx_rates_from_currency", "fx_rates", ["from_currency"])
    op.create_index("ix_fx_rates_rate_date", "fx_rates", ["rate_date"])
    op.create_index("ix_fx_rates_to_currency", "fx_rates", ["to_currency"])

    op.create_table(
        "benchmark_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("benchmark_id", sa.String(length=64), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("benchmark_id", "price_date", name="uq_benchmark_price_date"),
    )
    op.create_index("ix_benchmark_prices_batch_id", "benchmark_prices", ["batch_id"])
    op.create_index("ix_benchmark_prices_benchmark_id", "benchmark_prices", ["benchmark_id"])
    op.create_index("ix_benchmark_prices_price_date", "benchmark_prices", ["price_date"])

    op.create_table(
        "portfolio_daily_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.String(length=64), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("market_value", sa.Float(), nullable=False),
        sa.Column("daily_return", sa.Float(), nullable=True),
        sa.Column("cumulative_return", sa.Float(), nullable=False),
        sa.Column("positions_count", sa.Integer(), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.portfolio_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portfolio_id", "snapshot_date", name="uq_snapshot_portfolio_date"),
    )
    op.create_index("ix_portfolio_daily_snapshots_portfolio_id", "portfolio_daily_snapshots", ["portfolio_id"])
    op.create_index("ix_portfolio_daily_snapshots_snapshot_date", "portfolio_daily_snapshots", ["snapshot_date"])


def downgrade() -> None:
    op.drop_table("portfolio_daily_snapshots")
    op.drop_table("benchmark_prices")
    op.drop_table("fx_rates")

