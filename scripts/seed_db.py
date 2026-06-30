from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.ingestion_service import seed_sample_data


def main() -> None:
    init_db()
    with SessionLocal() as db:
        results = seed_sample_data(db, force=True)
        for result in results:
            print(result.model_dump())


if __name__ == "__main__":
    main()
