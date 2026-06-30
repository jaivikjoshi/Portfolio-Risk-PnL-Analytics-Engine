from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.schemas.returns import ReturnsResponse
from app.services.reporting_service import get_returns

router = APIRouter(prefix="/portfolios/{portfolio_id}/returns", tags=["returns"])


@router.get("", response_model=ReturnsResponse)
def returns(
    portfolio_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> ReturnsResponse:
    try:
        return ReturnsResponse(
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            returns=get_returns(
                db,
                portfolio_id=portfolio_id,
                start_date=start_date,
                end_date=end_date,
            ),
        )
    except AnalyticsError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id}) from exc

