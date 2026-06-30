# Calculation Methods

This project prioritizes deterministic, explainable analytics over black-box finance math. Every reported figure should be traceable to trades, prices, and a documented formula.

## Position Quantity

```text
quantity = sum(buy quantities) - sum(sell quantities)
```

Short selling is disabled by default. A sell that exceeds current holdings is reported as a critical validation issue.

## Weighted Average Cost

The MVP uses weighted average cost for open positions.

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

