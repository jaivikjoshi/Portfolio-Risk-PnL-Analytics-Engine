"""Initial portfolio analytics schema.

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260630_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portfolio_id"),
    )
    op.create_index("ix_portfolios_portfolio_id", "portfolios", ["portfolio_id"])

    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("instrument_id", sa.String(length=64), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_class", sa.String(length=64), nullable=False),
        sa.Column("sector", sa.String(length=128), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("exchange", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id"),
    )
    op.create_index("ix_instruments_instrument_id", "instruments", ["instrument_id"])
    op.create_index("ix_instruments_ticker", "instruments", ["ticker"])

    op.create_table(
        "ingestion_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rows_received", sa.Integer(), nullable=False),
        sa.Column("rows_loaded", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id"),
    )
    op.create_index("ix_ingestion_batches_batch_id", "ingestion_batches", ["batch_id"])
    op.create_index("ix_ingestion_batches_source_hash", "ingestion_batches", ["source_hash"])
    op.create_index("ix_ingestion_batches_source_type", "ingestion_batches", ["source_type"])

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trade_id", sa.String(length=96), nullable=False),
        sa.Column("portfolio_id", sa.String(length=64), nullable=False),
        sa.Column("instrument_id", sa.String(length=64), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("fees", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.instrument_id"]),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.portfolio_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trade_id", name="uq_trades_trade_id"),
    )
    op.create_index("ix_trades_batch_id", "trades", ["batch_id"])
    op.create_index("ix_trades_instrument_id", "trades", ["instrument_id"])
    op.create_index("ix_trades_portfolio_id", "trades", ["portfolio_id"])
    op.create_index("ix_trades_trade_date", "trades", ["trade_date"])
    op.create_index("ix_trades_trade_id", "trades", ["trade_id"])

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("instrument_id", sa.String(length=64), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.instrument_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id", "price_date", name="uq_prices_instrument_date"),
    )
    op.create_index("ix_prices_batch_id", "prices", ["batch_id"])
    op.create_index("ix_prices_instrument_id", "prices", ["instrument_id"])
    op.create_index("ix_prices_price_date", "prices", ["price_date"])

    op.create_table(
        "validation_issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.String(length=128), nullable=False),
        sa.Column("batch_id", sa.String(length=96), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("rule_code", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("source_row", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["ingestion_batches.batch_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_id"),
    )
    op.create_index("ix_validation_issues_batch_id", "validation_issues", ["batch_id"])
    op.create_index("ix_validation_issues_entity_id", "validation_issues", ["entity_id"])
    op.create_index("ix_validation_issues_entity_type", "validation_issues", ["entity_type"])
    op.create_index("ix_validation_issues_issue_id", "validation_issues", ["issue_id"])
    op.create_index("ix_validation_issues_rule_code", "validation_issues", ["rule_code"])
    op.create_index("ix_validation_issues_severity", "validation_issues", ["severity"])


def downgrade() -> None:
    op.drop_table("validation_issues")
    op.drop_table("prices")
    op.drop_table("trades")
    op.drop_table("ingestion_batches")
    op.drop_table("instruments")
    op.drop_table("portfolios")

