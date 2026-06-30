from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import bad_request
from app.schemas.ingestion import IngestionResult
from app.services.ingestion_service import ingest_upload, seed_sample_data

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/seed", response_model=list[IngestionResult])
def seed_data(force: bool = Query(True), db: Session = Depends(get_db)) -> list[IngestionResult]:
    try:
        return seed_sample_data(db, force=force)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@router.post("/{source_type}", response_model=IngestionResult)
async def upload_source(
    source_type: str,
    force: bool = Query(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IngestionResult:
    try:
        content = await file.read()
        return await ingest_upload(
            db,
            source_type=source_type,
            filename=file.filename or f"{source_type}.csv",
            content=content,
            force=force,
        )
    except ValueError as exc:
        raise bad_request(str(exc), {"source_type": source_type}) from exc

