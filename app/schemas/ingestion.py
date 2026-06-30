from __future__ import annotations

from pydantic import BaseModel


class IngestionResult(BaseModel):
    batch_id: str
    status: str
    source_type: str
    rows_received: int
    rows_loaded: int
    rows_rejected: int
    issues_count: int

