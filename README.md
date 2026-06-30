# Portfolio Risk & PnL Analytics Engine

A backend-first portfolio analytics engine for ingesting trades and prices, validating portfolio data quality, and reporting positions, realized PnL, unrealized PnL, returns, exposures, and risk metrics through FastAPI.

## What It Does

- Loads portfolio, instrument, trade, and price CSVs into a normalized SQL database.
- Tracks ingestion batches, source hashes, row counts, rejected rows, and validation issues.
- Validates missing prices, invalid rows, duplicate trades, unknown instruments, and sell quantity breaks.
- Computes weighted-average-cost positions, realized PnL, unrealized PnL, total PnL, daily returns, exposures, volatility, Sharpe ratio, Sortino ratio, max drawdown, and historical VaR.
- Supports weighted-average, FIFO, and LIFO PnL views.
- Converts non-base-currency positions with seeded FX rates.
- Compares portfolio returns against a seeded SPY benchmark.
- Persists daily portfolio value snapshots for repeatable reporting.
- Serves a lightweight HTML risk dashboard.
- Exposes analytics through documented FastAPI endpoints.
- Includes deterministic tests for the financial math and API workflow.

## Demo in 60 Seconds

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/seed_db.py
python scripts/run_validation.py
python scripts/generate_report.py
```

Expected seeded PnL headline:

```text
realized_pnl: 344.6
unrealized_pnl: 562.41
total_pnl: 907.01
```

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL-ready schema
- SQLite fallback for local quickstart and tests
- Pandas
- NumPy
- Pytest

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/seed_db.py
python scripts/run_validation.py
uvicorn app.api.main:app --reload
```

Open:

- API health: http://localhost:8000/health
- OpenAPI docs: http://localhost:8000/docs

## Docker Quickstart

Docker is optional. If Docker is installed:

```bash
docker compose up --build
```

The API runs at http://localhost:8000 and PostgreSQL runs on port `5432`.

## Demo API Flow

Seed the sample portfolio:

```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/seed"
```

Run validation:

```bash
curl -X POST "http://localhost:8000/api/v1/validation/run"
curl "http://localhost:8000/api/v1/validation/issues"
```

Query positions:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/positions?as_of=2026-01-10"
```

Query PnL:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10"
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10&cost_method=fifo"
```

Query exposure:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/exposures?as_of=2026-01-10&group_by=sector"
```

Query returns and risk:

```bash
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/returns?start_date=2026-01-02&end_date=2026-01-10"
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/risk?start_date=2026-01-02&end_date=2026-01-10"
curl "http://localhost:8000/api/v1/portfolios/P_MAIN/benchmark?benchmark_id=SPY&start_date=2026-01-02&end_date=2026-01-10"
curl -X POST "http://localhost:8000/api/v1/portfolios/P_MAIN/snapshots?start_date=2026-01-02&end_date=2026-01-10"
```

Dashboard:

```text
http://localhost:8000/dashboard/P_MAIN?start_date=2026-01-02&as_of=2026-01-10
```

## Golden PnL Example

The test suite includes a hand-checkable trade sequence:

| Date | Action | Quantity | Price | Fee |
| --- | --- | ---: | ---: | ---: |
| 2026-01-02 | Buy | 100 | 10.00 | 1.00 |
| 2026-01-03 | Buy | 50 | 12.00 | 1.00 |
| 2026-01-05 | Sell | 80 | 15.00 | 1.00 |
| 2026-01-10 | Mark | 70 | 14.00 | 0.00 |

Expected values:

- Quantity: `70`
- Average cost: `10.68`
- Cost basis: `747.60`
- Realized PnL: `344.60`
- Unrealized PnL: `232.40`
- Total PnL: `577.00`

## API Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Service health check |
| `POST /api/v1/ingestion/seed` | Load sample data |
| `POST /api/v1/ingestion/{source_type}` | Upload CSV data |
| `POST /api/v1/validation/run` | Run portfolio validation checks |
| `GET /api/v1/validation/issues` | List validation issues |
| `GET /api/v1/portfolios/{portfolio_id}/positions` | Position report |
| `GET /api/v1/portfolios/{portfolio_id}/pnl` | Realized/unrealized PnL report |
| `GET /api/v1/portfolios/{portfolio_id}/returns` | Daily and cumulative returns |
| `GET /api/v1/portfolios/{portfolio_id}/exposures` | Exposure by instrument, sector, currency, or asset class |
| `GET /api/v1/portfolios/{portfolio_id}/risk` | Volatility, Sharpe, Sortino, drawdown, VaR |
| `GET /api/v1/portfolios/{portfolio_id}/benchmark` | Compare portfolio returns to a benchmark |
| `POST /api/v1/portfolios/{portfolio_id}/snapshots` | Persist daily portfolio value snapshots |
| `GET /dashboard/{portfolio_id}` | Lightweight HTML risk dashboard |

## Data Model

Core tables:

- `portfolios`
- `instruments`
- `trades`
- `prices`
- `fx_rates`
- `benchmark_prices`
- `portfolio_daily_snapshots`
- `ingestion_batches`
- `validation_issues`

The schema is defined in SQLAlchemy models and captured in Alembic migration `20260630_0001_initial_schema`.

## Documentation

- [PRD](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API examples](docs/API_EXAMPLES.md)
- [Calculation methods](docs/CALCULATION_METHODS.md)
- [Sample outputs](docs/SAMPLE_OUTPUTS.md)

## Validation Rules

The engine records structured validation issues with severity, rule code, entity ID, source file, and row number when available.

Implemented rules include:

- `INVALID_ROW`
- `MISSING_COLUMNS`
- `DUPLICATE_TRADE_ID`
- `INVALID_TRADE_VALUES`
- `UNKNOWN_INSTRUMENT`
- `MISSING_PRICE`
- `SELL_EXCEEDS_POSITION`

## Run Tests

```bash
pytest
```

Current tests cover:

- Weighted average cost
- Realized PnL
- Unrealized PnL
- Exposure grouping
- Daily returns
- Risk metrics
- Validation issue creation
- End-to-end API seed/report flow

## Resume Traceability

| Resume Claim | Project Evidence |
| --- | --- |
| End-to-end portfolio reporting | Seed data, FastAPI endpoints, integration tests |
| Positions | `app/analytics/positions.py`, `/positions` endpoint |
| Realized PnL | `app/analytics/pnl.py`, golden dataset tests |
| Unrealized PnL | Position valuation tests and `/pnl` endpoint |
| FIFO/LIFO accounting | `app/analytics/tax_lots.py`, `cost_method` query parameter |
| FX support | `app/analytics/fx.py`, seeded CAD Shopify position |
| Benchmark comparison | `app/analytics/benchmark.py`, `/benchmark` endpoint |
| Persisted reporting snapshots | `portfolio_daily_snapshots`, `/snapshots` endpoint |
| Returns | `app/analytics/returns.py`, `/returns` endpoint |
| Asset exposure | `app/analytics/exposures.py`, `/exposures` endpoint |
| Python, SQL, Pandas, NumPy | Analytics modules, SQLAlchemy models, migrations |
| PostgreSQL schemas | Docker Compose, Alembic migration, SQLAlchemy constraints |
| FastAPI endpoints | `app/api/routes/` |
| Missing prices and invalid trades | Validation service and bad sample datasets |
| Inconsistent positions | `SELL_EXCEEDS_POSITION` validation rule |

## Repository

Canonical GitHub repository:

https://github.com/jaivikjoshi/Portfolio-Risk-PnL-Analytics-Engine
