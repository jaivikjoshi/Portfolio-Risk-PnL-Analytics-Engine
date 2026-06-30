from __future__ import annotations

from app.db.base import Base
from app.db.models import IngestionBatch, Instrument, Portfolio, Price, Trade, ValidationIssue
from app.db.session import engine

__all__ = [
    "IngestionBatch",
    "Instrument",
    "Portfolio",
    "Price",
    "Trade",
    "ValidationIssue",
    "init_db",
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

