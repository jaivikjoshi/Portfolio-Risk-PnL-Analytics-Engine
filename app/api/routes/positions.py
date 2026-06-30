from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.schemas.positions import PositionsResponse
from app.services.reporting_service import get_positions

router = APIRouter(prefix="/portfolios/{portfolio_id}/positions", tags=["positions"])


@router.get("", response_model=PositionsResponse)
def positions(
    portfolio_id: str,
    as_of: date = Query(...),
    db: Session = Depends(get_db),
) -> PositionsResponse:
    try:
        return PositionsResponse(
            portfolio_id=portfolio_id,
            as_of=as_of,
            positions=get_positions(db, portfolio_id=portfolio_id, as_of=as_of),
        )
    except AnalyticsError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id, "as_of": str(as_of)}) from exc

