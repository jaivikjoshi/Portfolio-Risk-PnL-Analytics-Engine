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
  "unrealized_pnl": 489.4,
  "total_pnl": 834.0
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
