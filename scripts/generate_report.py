from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from pprint import pprint

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.reporting_service import get_exposures, get_pnl, get_positions, get_risk


def main() -> None:
    init_db()
    with SessionLocal() as db:
        portfolio_id = "P_MAIN"
        as_of = date(2026, 1, 10)
        pprint({"positions": get_positions(db, portfolio_id=portfolio_id, as_of=as_of)})
        pprint(
            {
                "pnl": get_pnl(
                    db,
                    portfolio_id=portfolio_id,
                    start_date=date(2026, 1, 1),
                    end_date=as_of,
                )
            }
        )
        pprint({"exposures": get_exposures(db, portfolio_id=portfolio_id, as_of=as_of, group_by="sector")})
        pprint(
            {
                "risk": get_risk(
                    db,
                    portfolio_id=portfolio_id,
                    start_date=date(2026, 1, 2),
                    end_date=as_of,
                )
            }
        )


if __name__ == "__main__":
    main()
