from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.schemas.pnl import PnlResponse
from app.services.reporting_service import get_pnl

router = APIRouter(prefix="/portfolios/{portfolio_id}/pnl", tags=["pnl"])


@router.get("", response_model=PnlResponse)
def pnl(
    portfolio_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    cost_method: str = Query("weighted_average", pattern="^(weighted_average|fifo|lifo)$"),
    db: Session = Depends(get_db),
) -> PnlResponse:
    try:
        result = get_pnl(
            db,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            cost_method=cost_method,
        )
        return PnlResponse(portfolio_id=portfolio_id, start_date=start_date, end_date=end_date, **result)
    except AnalyticsError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id}) from exc
