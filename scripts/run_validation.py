from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.validation_service import run_validation


def main() -> None:
    init_db()
    with SessionLocal() as db:
        print(run_validation(db))


if __name__ == "__main__":
    main()
