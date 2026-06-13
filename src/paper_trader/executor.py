from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from paper_trader.strategy.sma_crossover import Signal


def submit_market_order(
    client: TradingClient,
    symbol: str,
    signal: Signal,
    *,
    qty: int | None = None,
    notional: float | None = None,
) -> str:
    side = OrderSide.BUY if signal == Signal.BUY else OrderSide.SELL
    order = MarketOrderRequest(
        symbol=symbol,
        side=side,
        time_in_force=TimeInForce.DAY,
        qty=qty,
        notional=notional,
    )
    submitted = client.submit_order(order)
    return str(submitted.id)
