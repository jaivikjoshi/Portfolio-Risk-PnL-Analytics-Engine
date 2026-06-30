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
  "unrealized_pnl": 562.41,
  "total_pnl": 907.01,
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

FIFO excerpt:

```json
{
  "realized_pnl": 398.2,
  "unrealized_pnl": 510.814,
  "total_pnl": 909.014
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
  "total_market_value": 6509.5,
  "exposures": [
    {
      "group": "Technology",
      "market_value": 2949.5,
      "exposure_percentage": 0.453107
    },
    {
      "group": "Rates",
      "market_value": 2300.0,
      "exposure_percentage": 0.35333
    },
    {
      "group": "Financials",
      "market_value": 1260.0,
      "exposure_percentage": 0.193563
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
  "annualized_volatility": 5.199128,
  "sharpe_ratio": 9.63379,
  "sortino_ratio": null,
  "max_drawdown": -0.291667,
  "var_95": -1200.35896
}
```

## FX Position

The seeded portfolio includes Shopify in CAD:

```json
{
  "ticker": "SHOP",
  "currency": "CAD",
  "fx_rate": 0.745,
  "market_value": 1100.0,
  "market_value_base": 819.5,
  "unrealized_pnl": 98.0,
  "unrealized_pnl_base": 73.01
}
```

## Benchmark

Response excerpt:

```json
{
  "benchmark_id": "SPY",
  "observations": 9,
  "ending_active_return": 2.233917
}
```

## Snapshots

Response excerpt:

```json
{
  "snapshots_created": 9,
  "latest_market_value": 6509.5,
  "latest_positions_count": 5
}
```
