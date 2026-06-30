# Calculation Methods

This project prioritizes deterministic, explainable analytics over black-box finance math. Every reported figure should be traceable to trades, prices, and a documented formula.

## Position Quantity

```text
quantity = sum(buy quantities) - sum(sell quantities)
```

Short selling is disabled by default. A sell that exceeds current holdings is reported as a critical validation issue.

## Weighted Average Cost

The default PnL method uses weighted average cost for open positions.

For buys:

```text
new_quantity = old_quantity + buy_quantity
new_cost_basis = old_cost_basis + buy_quantity * buy_price + buy_fees
average_cost = new_cost_basis / new_quantity
```

For sells:

```text
realized_pnl = (sell_price - average_cost_before_sell) * sell_quantity - sell_fees
remaining_cost_basis = old_cost_basis - average_cost_before_sell * sell_quantity
```

## Unrealized PnL

```text
unrealized_pnl = (market_price - average_cost) * open_quantity
```

Market price is the latest available close on or before the requested report date.

## Total PnL

```text
total_pnl = realized_pnl + unrealized_pnl
```

## FIFO and LIFO

The PnL endpoint also supports tax-lot style reporting:

```text
GET /api/v1/portfolios/P_MAIN/pnl?...&cost_method=fifo
GET /api/v1/portfolios/P_MAIN/pnl?...&cost_method=lifo
```

FIFO consumes the oldest open buy lots first. LIFO consumes the newest open buy lots first. Buy fees are allocated into per-unit cost. Sell fees reduce realized PnL.

For the seeded AAPL example:

| Method | Realized PnL | Unrealized PnL |
| --- | ---: | ---: |
| weighted_average | 344.60 | 232.40 |
| fifo | 398.20 | 178.80 |
| lifo | 297.70 | 279.30 |

## FX Conversion

Positions retain local-currency values and also report base-currency values.

```text
market_value_base = market_value_local * latest_fx_rate
unrealized_pnl_base = unrealized_pnl_local * latest_fx_rate
```

The seeded portfolio includes Shopify in CAD and converts it to the portfolio base currency, USD, using the latest CAD/USD rate on or before the report date.

## Daily Returns

The current MVP treats the seeded portfolio as fully invested with no external cash-flow ledger.

```text
daily_return = (market_value_today - market_value_yesterday) / market_value_yesterday
```

The return is `null` when the previous market value is zero.

## Exposure

```text
exposure_percentage = group_market_value / total_portfolio_market_value
```

Supported groups:

- instrument
- asset class
- sector
- currency

## Risk Metrics

Volatility:

```text
annualized_volatility = std(daily_returns) * sqrt(252)
```

Sharpe ratio:

```text
sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
```

Sortino ratio:

```text
sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation
```

Max drawdown:

```text
drawdown = portfolio_value / running_peak - 1
max_drawdown = min(drawdown)
```

Historical VaR:

```text
var_95 = percentile(daily_returns, 5) * latest_portfolio_value
```

## Benchmark Comparison

Benchmark comparison aligns portfolio cumulative returns and benchmark cumulative returns by date.

```text
active_return = portfolio_cumulative_return - benchmark_cumulative_return
```

The seeded benchmark is `SPY`.

## Daily Snapshots

The snapshot endpoint persists daily portfolio values so repeated reports can reuse audited daily records.

Stored fields:

- market value
- daily return
- cumulative return
- positions count
- base currency
