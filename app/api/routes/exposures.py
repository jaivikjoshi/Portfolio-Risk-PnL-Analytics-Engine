from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.schemas.exposures import ExposuresResponse
from app.services.reporting_service import get_exposures

router = APIRouter(prefix="/portfolios/{portfolio_id}/exposures", tags=["exposures"])


@router.get("", response_model=ExposuresResponse)
def exposures(
    portfolio_id: str,
    as_of: date = Query(...),
    group_by: str = Query("sector"),
    db: Session = Depends(get_db),
) -> ExposuresResponse:
    try:
        result = get_exposures(db, portfolio_id=portfolio_id, as_of=as_of, group_by=group_by)
        return ExposuresResponse(portfolio_id=portfolio_id, as_of=as_of, group_by=group_by, **result)
    except (AnalyticsError, ValueError) as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id, "group_by": group_by}) from exc

