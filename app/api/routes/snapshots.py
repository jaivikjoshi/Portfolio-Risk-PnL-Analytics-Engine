from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import bad_request
from app.schemas.snapshots import SnapshotOut, SnapshotRunResponse
from app.services.snapshot_service import generate_snapshots

router = APIRouter(prefix="/portfolios/{portfolio_id}/snapshots", tags=["snapshots"])


@router.post("", response_model=SnapshotRunResponse)
def snapshots(
    portfolio_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> SnapshotRunResponse:
    try:
        records = generate_snapshots(
            db,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
        )
        return SnapshotRunResponse(
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            snapshots_created=len(records),
            snapshots=[SnapshotOut.model_validate(record, from_attributes=True) for record in records],
        )
    except ValueError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id}) from exc

