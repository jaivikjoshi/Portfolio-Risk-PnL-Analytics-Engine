from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics.benchmark import compare_to_benchmark
from app.api.dependencies import get_db
from app.core.exceptions import AnalyticsError, bad_request
from app.db.repositories import list_benchmark_prices
from app.schemas.benchmark import BenchmarkComparisonResponse
from app.services.reporting_service import get_returns

router = APIRouter(prefix="/portfolios/{portfolio_id}/benchmark", tags=["benchmark"])


@router.get("", response_model=BenchmarkComparisonResponse)
def benchmark(
    portfolio_id: str,
    benchmark_id: str = Query("SPY"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> BenchmarkComparisonResponse:
    try:
        portfolio_returns = get_returns(
            db, portfolio_id=portfolio_id, start_date=start_date, end_date=end_date
        )
        benchmark_prices = [
            {
                "benchmark_id": price.benchmark_id,
                "price_date": price.price_date,
                "close_price": price.close_price,
                "currency": price.currency,
            }
            for price in list_benchmark_prices(db, benchmark_id, start_date, end_date)
        ]
        result = compare_to_benchmark(
            portfolio_returns,
            benchmark_prices,
            start_date=start_date,
            end_date=end_date,
        )
        return BenchmarkComparisonResponse(
            portfolio_id=portfolio_id,
            benchmark_id=benchmark_id,
            **result,
        )
    except AnalyticsError as exc:
        raise bad_request(str(exc), {"portfolio_id": portfolio_id, "benchmark_id": benchmark_id}) from exc

