from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.analytics.exposures import compute_exposures
from app.analytics.pnl import compute_pnl
from app.analytics.positions import compute_position_states
from app.analytics.returns import compute_returns
from app.analytics.risk import compute_risk_metrics
from app.core.config import settings
from app.core.exceptions import AnalyticsError
from app.db.models import FxRate, Instrument, Price, Trade
from app.db.repositories import get_portfolio, list_fx_rates, list_instruments, list_prices, list_trades


def _trade_dict(trade: Trade) -> dict[str, Any]:
    return {
        "trade_id": trade.trade_id,
        "portfolio_id": trade.portfolio_id,
        "instrument_id": trade.instrument_id,
        "trade_date": trade.trade_date,
        "side": trade.side,
        "quantity": trade.quantity,
        "price": trade.price,
        "fees": trade.fees,
        "currency": trade.currency,
    }


def _price_dict(price: Price) -> dict[str, Any]:
    return {
        "instrument_id": price.instrument_id,
        "price_date": price.price_date,
        "close_price": price.close_price,
        "currency": price.currency,
    }


def _fx_dict(rate: FxRate) -> dict[str, Any]:
    return {
        "rate_date": rate.rate_date,
        "from_currency": rate.from_currency,
        "to_currency": rate.to_currency,
        "rate": rate.rate,
    }


def _instrument_dict(instrument: Instrument) -> dict[str, Any]:
    return {
        "instrument_id": instrument.instrument_id,
        "ticker": instrument.ticker,
        "name": instrument.name,
        "asset_class": instrument.asset_class,
        "sector": instrument.sector,
        "currency": instrument.currency,
        "exchange": instrument.exchange,
    }


def _load_inputs(db: Session, portfolio_id: str, end_date: date) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]], str
]:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        raise AnalyticsError(f"Portfolio '{portfolio_id}' was not found.")

    trades = [_trade_dict(trade) for trade in list_trades(db, portfolio_id=portfolio_id, end_date=end_date)]
    prices = [_price_dict(price) for price in list_prices(db, end_date=end_date)]
    instruments = {i.instrument_id: _instrument_dict(i) for i in list_instruments(db)}
    fx_rates = [_fx_dict(rate) for rate in list_fx_rates(db, end_date=end_date)]
    return trades, prices, instruments, fx_rates, portfolio.base_currency


def get_positions(db: Session, *, portfolio_id: str, as_of: date) -> list[dict[str, Any]]:
    trades, prices, instruments, fx_rates, base_currency = _load_inputs(db, portfolio_id, as_of)
    return compute_position_states(
        trades,
        prices,
        instruments,
        as_of=as_of,
        base_currency=base_currency,
        fx_rates=fx_rates,
        allow_short_selling=settings.allow_short_selling,
    )


def get_pnl(
    db: Session, *, portfolio_id: str, start_date: date, end_date: date, cost_method: str = "weighted_average"
) -> dict[str, Any]:
    trades, prices, instruments, fx_rates, base_currency = _load_inputs(db, portfolio_id, end_date)
    return compute_pnl(
        trades,
        prices,
        instruments,
        start_date=start_date,
        end_date=end_date,
        base_currency=base_currency,
        fx_rates=fx_rates,
        cost_method=cost_method,
        allow_short_selling=settings.allow_short_selling,
    )


def get_returns(
    db: Session, *, portfolio_id: str, start_date: date, end_date: date
) -> list[dict[str, Any]]:
    trades, prices, instruments, fx_rates, base_currency = _load_inputs(db, portfolio_id, end_date)
    return compute_returns(
        trades,
        prices,
        instruments,
        start_date=start_date,
        end_date=end_date,
        base_currency=base_currency,
        fx_rates=fx_rates,
        allow_short_selling=settings.allow_short_selling,
    )


def get_exposures(
    db: Session, *, portfolio_id: str, as_of: date, group_by: str
) -> dict[str, Any]:
    trades, prices, instruments, fx_rates, base_currency = _load_inputs(db, portfolio_id, as_of)
    return compute_exposures(
        trades,
        prices,
        instruments,
        as_of=as_of,
        group_by=group_by,
        base_currency=base_currency,
        fx_rates=fx_rates,
        allow_short_selling=settings.allow_short_selling,
    )


def get_risk(
    db: Session, *, portfolio_id: str, start_date: date, end_date: date
) -> dict[str, Any]:
    returns = get_returns(db, portfolio_id=portfolio_id, start_date=start_date, end_date=end_date)
    return compute_risk_metrics(returns, risk_free_rate=settings.risk_free_rate)
