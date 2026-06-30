# Sample Outputs

These outputs come from the seeded sample portfolio.

## Health

```json
{
  "status": "ok",
  "service": "Portfolio Risk PnL Analytics Engine"
}
```

## PnL

Request:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10"
```

Response excerpt:

```json
{
  "portfolio_id": "P_MAIN",
  "realized_pnl": 344.6,
  "unrealized_pnl": 489.4,
  "total_pnl": 834.0,
  "by_instrument": [
    {
      "instrument_id": "I_AAPL",
      "ticker": "AAPL",
      "realized_pnl": 344.6,
      "unrealized_pnl": 232.4,
      "total_pnl": 577.0
    }
  ]
}
```

## Sector Exposure

Request:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/exposures?as_of=2026-01-10&group_by=sector"
```

Response excerpt:

```json
{
  "total_market_value": 5690.0,
  "exposures": [
    {
      "group": "Rates",
      "market_value": 2300.0,
      "exposure_percentage": 0.404218
    },
    {
      "group": "Technology",
      "market_value": 2130.0,
      "exposure_percentage": 0.374341
    },
    {
      "group": "Financials",
      "market_value": 1260.0,
      "exposure_percentage": 0.221441
    }
  ]
}
```

## Risk

Request:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/risk?start_date=2026-01-02&end_date=2026-01-10"
```

Response excerpt:

```json
{
  "observations": 8,
  "annualized_volatility": 5.336389,
  "sharpe_ratio": 8.555233,
  "sortino_ratio": 14.803765,
  "max_drawdown": -0.291667,
  "var_95": -1112.44052
}
```

