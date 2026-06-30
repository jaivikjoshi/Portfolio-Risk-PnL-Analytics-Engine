# API Examples

## Seed

```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/seed"
```

## Positions

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/positions?as_of=2026-01-10"
```

## PnL

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10"
```

Expected headline values for the seeded portfolio:

```json
{
  "realized_pnl": 344.6,
  "unrealized_pnl": 562.41,
  "total_pnl": 907.01
}
```

Alternate cost method:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10&cost_method=fifo"
```

FIFO excerpt:

```json
{
  "realized_pnl": 398.2,
  "unrealized_pnl": 510.814,
  "total_pnl": 909.014
}
```

## Exposures

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/exposures?as_of=2026-01-10&group_by=sector"
```

## Risk

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/risk?start_date=2026-01-02&end_date=2026-01-10"
```

## Benchmark

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/benchmark?benchmark_id=SPY&start_date=2026-01-02&end_date=2026-01-10"
```

## Snapshots

```bash
curl -X POST "http://localhost:8000/api/v1/portfolios/P_MAIN/snapshots?start_date=2026-01-02&end_date=2026-01-10"
```

## Dashboard

```text
http://localhost:8000/dashboard/P_MAIN?start_date=2026-01-02&as_of=2026-01-10
```
