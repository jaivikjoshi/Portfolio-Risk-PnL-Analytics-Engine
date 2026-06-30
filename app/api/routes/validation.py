from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.validation import ValidationIssueOut, ValidationRunResult
from app.services.validation_service import list_issues, run_validation

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/run", response_model=ValidationRunResult)
def run(db: Session = Depends(get_db)) -> dict[str, int | str]:
    return run_validation(db)


@router.get("/issues", response_model=list[ValidationIssueOut])
def issues(
    severity: str | None = Query(None),
    rule_code: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_issues(db, severity=severity, rule_code=rule_code, limit=limit)

