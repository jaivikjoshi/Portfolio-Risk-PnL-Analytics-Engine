from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.schemas.risk import RiskResponse
from app.services.reporting_service import get_risk

router = APIRouter(prefix="/portfolios/{portfolio_id}/risk", tags=["risk"])


@router.get("", response_model=RiskResponse)
def risk(
    portfolio_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> RiskResponse:
    try:
        result = get_risk(db, portfolio_id=portfolio_id, start_date=start_date, end_date=end_date)
        return RiskResponse(portfolio_id=portfolio_id, start_date=start_date, end_date=end_date, **result)
    except AnalyticsError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id}) from exc

