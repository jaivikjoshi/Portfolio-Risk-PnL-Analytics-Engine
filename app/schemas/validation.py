from __future__ import annotations

from datetime import datetime

from app.schemas.common import ApiModel


class ValidationIssueOut(ApiModel):
    issue_id: str
    batch_id: str | None
    severity: str
    entity_type: str
    entity_id: str
    rule_code: str
    message: str
    source_file: str | None
    source_row: int | None
    created_at: datetime


class ValidationRunResult(ApiModel):
    status: str
    issues_created: int
    critical_count: int
    error_count: int
    warning_count: int

